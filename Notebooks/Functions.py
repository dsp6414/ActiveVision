import os
import time
import matplotlib.pyplot as plt
import numpy as np
import argparse
import noise

def vectorization(N_theta, N_orient, N_scale, N_phase, N_X, N_Y, rho):
    phi = np.zeros((N_theta, N_orient, N_scale, N_phase, N_X*N_Y))
    parameterfile = 'https://raw.githubusercontent.com/bicv/LogGabor/master/default_param.py'
    lg = LogGabor(parameterfile)
    lg.set_size((N_X, N_Y))
    params = {'sf_0': .1, 'B_sf': 2*lg.pe.B_sf,
              'theta': np.pi * 5 / 7., 'B_theta': 2*lg.pe.B_theta}
    phase = np.pi/4
    edge = lg.normalize(lg.invert(lg.loggabor(
        N_X/3, 3*N_Y/4, **params)*np.exp(-1j*phase)))

    for i_theta in range(N_theta):
        for i_orient in range(N_orient):
            for i_scale in range(N_scale):
                ecc = (1/rho)**(N_scale - i_scale)
                r = np.sqrt(N_X**2+N_Y**2) / 2 * ecc  # radius
                sf_0 = 0.5 * 0.03 / ecc
                x = N_X/2 + r * \
                    np.cos((i_orient+(i_scale % 2)*.5)*np.pi*2 / N_orient)
                y = N_Y/2 + r * \
                    np.sin((i_orient+(i_scale % 2)*.5)*np.pi*2 / N_orient)
                for i_phase in range(N_phase):
                    params = {'sf_0': sf_0, 'B_sf': lg.pe.B_sf,
                              'theta': i_theta*np.pi/N_theta, 'B_theta': np.pi/N_theta/2}
                    phase = i_phase * np.pi/2
                    phi[i_theta, i_orient, i_scale, i_phase, :] = lg.normalize(
                        lg.invert(lg.loggabor(x, y, **params)*np.exp(-1j*phase))).ravel()
    return phi

N_theta, N_orient, N_scale, N_phase, N_X, N_Y, rho = 6, 12, 5, 2, 128, 128, 1.61803

phi = vectorization(N_theta, N_orient, N_scale, N_phase, N_X, N_Y, rho)
phi_vector = phi.reshape((N_theta*N_orient*N_scale*N_phase, N_X*N_Y))
phi_plus = np.linalg.pinv(phi_vector)

energy = (phi**2).sum(axis=(0, 3))
energy /= energy.sum(axis=-1)[:, :, None]
energy_vector = energy.reshape((N_orient*N_scale, N_X*N_Y))
energy_plus = np.linalg.pinv(energy_vector)


def accuracy_128(i_offset, j_offset, N_pic=N_X, N_stim=55):
    center = (N_pic-N_stim)//2

    accuracy_128 = 0.1 * np.ones((N_pic, N_pic))

    accuracy_128[(center+i_offset):(center+N_stim+i_offset), (center+j_offset):(center+N_stim+j_offset)] = accuracy
    accuracy_128[int(center+i_offset):int(center+N_stim+i_offset),
                 int(center+j_offset):int(center+N_stim+j_offset)] = accuracy


    accuracy_LP = energy_vector @ np.ravel(accuracy_128)
    return accuracy_LP


def mnist_128(data, i_offset, j_offset, N_pic=N_X, N_stim=28, noise=True, noise_type='MotionCloud'):
    center = (N_pic-N_stim)//2
    data_128 = (data.min().numpy()) * np.ones((N_pic, N_pic))

    data_128[int(center+i_offset):int(center+N_stim+i_offset), int(center+j_offset):int(center+N_stim+j_offset)] = data

    if noise:
        if noise_type == 'MotionCloud':
            data_LP = phi_vector @ np.ravel(data_128 + MotionCloudNoise())
        elif noise_type == 'Perlin':
            data_LP = phi_vector @ np.ravel(
                data_128 + randomized_perlin_noise())
    else:
        data_LP = phi_vector @ np.ravel(data_128)
    return data_LP


def couples(data, i_offset, j_offset, device):
    data = data.to(device)
    v = mnist_128(data.cpu(), i_offset, j_offset)
    a = accuracy_128(i_offset, j_offset)
    return (v, a)


def minmax(value, border):
    value = max(value, -border)
    value = min(value, border)
    return int(value)


def sigmoid(values):
    values = 1 / (1 + ((1 / 0.1) - 1) * np.exp(-values))
    return values


def randomized_perlin_noise(shape=(128, 128), scale=10, octaves=6, persistence=0.5, lacunarity=2.0, base=0):
    noise_vector = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            noise_vector[i][j] = noise.pnoise2(i/scale,
                                               j/scale,
                                               octaves=int(
                                                   octave * abs(np.random.randn()))+1,
                                               persistence=persistence *
                                               abs(np.random.randn()),
                                               lacunarity=lacunarity *
                                               abs(np.random.randn()),
                                               repeatx=shape[0],
                                               repeaty=shape[1],
                                               base=base)
    return noise_vector


def MotionCloudNoise(sf_0=0.125, B_sf=3.):
    mc.N_X, mc.N_Y, mc.N_frame = 128, 128, 1
    fx, fy, ft = mc.get_grids(mc.N_X, mc.N_Y, mc.N_frame)
    name = 'static'
    env = mc.envelope_gabor(fx, fy, ft, sf_0=sf_0, B_sf=B_sf, B_theta=np.inf, V_X=0., V_Y=0., B_V=0, alpha=.5)

    z = mc.rectif(mc.random_cloud(env))
    z = z.reshape((mc.N_X, mc.N_Y))
    return z
   
    
def train(net, sample_size, optimizer=optimizer, vsize=N_theta*N_orient*N_scale*N_phase, asize=N_orient*N_scale, offset_std=10, offset_max=25, verbose=1):
    t_start = time.time()
    if verbose: print('Starting training...')
    for batch_idx, (data, label) in enumerate(data_loader):
        input, a_data = np.zeros((sample_size, 1, vsize)), np.zeros(
            (sample_size, 1, asize))
        target = np.zeros((sample_size, asize))
        for idx in range(sample_size):

            i_offset, j_offset = minmax(np.random.randn()*offset_std, offset_max), minmax(np.random.randn()*offset_std, offset_max)
            input[idx, 0, :], a_data[idx, 0, :] = couples(data[idx, 0, :], i_offset, j_offset, device)
            target[idx, :] = a_data[idx, 0, :]

        input, target = Variable(torch.FloatTensor(input)), Variable(torch.FloatTensor(a_data))

        prediction = net(input)
        loss = loss_func(prediction, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if verbose and batch_idx % 100 == 0:
            print('[{}/{}] Loss: {} Time: {:.2f} mn'.format(
                batch_idx*sample_size, len(data_loader.dataset),
                loss.data.numpy(), (time.time()-t_start)/60))
    return net


def test(net, sample_size, optimizer=optimizer, vsize=N_theta*N_orient*N_scale*N_phase, asize=N_orient*N_scale, offset_std=10, offset_max=25):
    for batch_idx, (data, label) in enumerate(data_loader):
        input, a_data = np.zeros((sample_size, 1, vsize)), np.zeros(
            (sample_size, 1, asize))
        target = np.zeros((sample_size, asize))
        for idx in range(sample_size):

            i_offset, j_offset = minmax(np.random.randn()*offset_std, offset_max), minmax(np.random.randn()*offset_std, offset_max)
            input[idx, 0, :], a_data[idx, 0, :] = couples(data[idx, 0, :], i_offset, j_offset, device)
            target[idx, :] = a_data[idx, 0, :]

        input = Variable(torch.FloatTensor(input))
        target = Variable(torch.FloatTensor(a_data))

        prediction = net(input)
        loss = loss_func(prediction, target)

    return loss.data.numpy()


def eval_sacc(vsize=N_theta*N_orient*N_scale*N_phase, asize=N_orient*N_scale, N_pic=N_X, sacc_lim=5, fovea_size=10, offset_std=10, offset_max=25, fig_type='cmap'):
    for batch_idx, (data, label) in enumerate(data_loader):
        data = data.to(device)
        i_offset = minmax(np.random.randn()*offset_std, offset_max)
        j_offset = minmax(np.random.randn()*offset_std, offset_max)
        print('Stimulus position: ({},{})'.format(i_offset, j_offset))
        a_data_in_fovea = False
        sacc_count = 0

        while not a_data_in_fovea:
            input, a_data = np.zeros((1, 1, vsize)), np.zeros((1, 1, asize))
            input[0, 0, :], a_data[0, 0, :] = couples(data[0, 0, :], i_offset, j_offset, device)
            input, a_data = Variable(torch.FloatTensor(input)), Variable(torch.FloatTensor(a_data))
            input, a_data = Variable(torch.FloatTensor(input)), Variable(torch.FloatTensor(a_data))

            input = Variable(torch.FloatTensor(input))
            a_data = Variable(torch.FloatTensor(a_data))

            prediction = net(input)
            pred_data = prediction.data.numpy()[-1][-1]

            if fig_type == 'cmap':
                image = energy_plus @ pred_data
                image_reshaped = image.reshape(N_pic, N_pic)

                fig, ax = plt.subplots(figsize=(13, 10.725))
                cmap = ax.pcolor(np.arange(-(N_pic/2), (N_pic/2)),
                                 np.arange(-(N_pic/2), (N_pic/2)), image_reshaped)
                fig.colorbar(cmap)
                plt.axvline(j_offset, c='k')
                plt.axhline(i_offset, c='k')

                for i_pred in range(0, N_pic):
                    for j_pred in range(0, N_pic):
                        if image_reshaped[i_pred][j_pred] == image_reshaped.max():
                            i_hat, j_hat = i_pred-(N_pic/2), j_pred-(N_pic/2)
                            print('Position prediction: ({},{})'.format(
                                i_hat, j_hat))
                            if fig_type == 'cmap':
                                plt.axvline(j_hat, c='r')
                                plt.axhline(i_hat, c='r')
                            break

                # check if number of saccades is beyond threshold
                if sacc_count == sacc_lim:
                    print('Stimulus position not found, break')
                    break

                # saccades
                i_offset, j_offset = (i_offset - i_hat), (j_offset - j_hat)
                sacc_count += 1
                print('Stimulus position after saccade: ({}, {})'.format(i_offset, j_offset))

                # check if the image position is predicted within the fovea
                if i_hat <= (fovea_size/2) and j_hat <= (fovea_size/2):
                    if i_hat >= -(fovea_size/2) and j_hat >= -(fovea_size/2):
                        a_data_in_fovea = True
                        print('a_data predicted in fovea, stopping the saccadic exploration')

            if fig_type == 'log':
                code = energy_plus @ pred_data
                global_energy = energy_vector @ code
                global_energy = global_energy.reshape(N_scale, N_orient)

                log_r_a_data = 1 + \
                    np.log(np.sqrt(i_offset**2 + j_offset**2) /
                           np.sqrt(N_X**2 + N_Y**2) / 2) / 5
                if j_offset != 0:
                    theta_a_data = np.arctan(-i_offset / j_offset)
                else:
                    theta_a_data = np.sign(-i_offset) * np.pi/2
                print('a_data position (log_r, theta) = ({},{})'.format(log_r_a_data,
                                                                        theta_a_data))
                log_r, theta = np.meshgrid(np.linspace(0, 1, N_scale+1), np.linspace(-np.pi*.625, np.pi*1.375, N_orient+1))

                fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
                ax.pcolor(theta, log_r, np.fliplr(global_energy))
                ax.plot(theta_a_data, log_r_a_data, 'r+')

                for n_orient in range(N_orient):
                    for n_scale in range(N_scale):
                        if global_energy[n_orient][n_scale] == np.max(global_energy):
                            print('Position prediction (orient, scale) = ({},{})'.format(
                                n_orient, n_scale))

                a_data_in_fovea = True

        print('*' * 50)
        return prediction