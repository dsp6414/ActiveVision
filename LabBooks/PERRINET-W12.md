# 2018-05-28
---
Pas de travail fourni aujourd'hui, participation aux Cordées de la Réussite en tant qu'étudiant encadrant.

# 2018-05-29
---
Laurent a créé un [modèle ML](https://github.com/laurentperrinet/CatchTheEye) simple qui obtient d'excellentes performances sur un problème similaire au notre (fork du travail d'[Anaïs et Nicolas](https://github.com/anaisbrgs/StageL3)).  
Il faut que je récupère son script Regard.py pour intégrer notamment la méthode dans mon travail.  

J'ai du installer la libraire easydict pour pouvoir faire tourner Regard.py :

    pip3 install --user easydict
    
# 2018-05-31
---
Pour pouvoir écrire le rapport, j'ai voulu fixer un stade de développement du modèle et écrire les résultats autour de ses performances. Problème: j'ai voulu me fixer sur 2018_05_23_classification_BCELoss parce que dans mes souvenirs il fonctionnait bien, mais en faisant tourner un apprentissage cette nuit je vois qu'il ne converge pas!

# 2018-06-01
---
J'ai peut-être trouvé la raison pour laquelle le modèle ne semble pas apprendre : les images MNIST que l'on utilise ont des valeurs entre (environ) -1 et 3, alors que l'image produite après passage dans le filtre rétinien comprends des valeurs entre (environ) -160 et 160 (sans bruit ajouté).  
C'est certainement cette différence d'echelle qui fait qu'on n'observe pas de convergence pendant l'apprentissage et qu'on ne voit pas le stimulus lors de la reconstruction graphique "filtre logpolar classique + image" (2018-05-21_LogPol_figures.ipynb)  

Le problème provenait de la normalisation qu'on avait implanté rapidement :

    > Where.py
    data_retina -= data_retina.mean()
    data_retina /= data_retina.std()
    data_retina *= std
    data_retina += mean
    
En retirant ces 4 lignes, on peut de nouveau observer le stimulus dans l'image post-filtre rétinien. Je suis en train de tester l'apprentissage pour voir si ça à aussi débloqué cette situation.


---
# To Do

### Modèle
+ ~~Recréer la carte d'accuracy en présence de bruit -> Script à modifier: 2018-04-27_classifier_noised.ipynb~~ -> Avons décidé avec Laurent de ne pas intégrer de bruit dans ces données 
+ Créer une carte de certitude persistente et mise à jour après chaque saccade
+ Intégrer le calcul GPU aux nouveaux scripts -> Cf notes 2018-05-24
+ Réaliser des benchmarking pour choisir les paramètres optimaux pour le modèle
    + learning rate
+ Ne garder que N_pic ou N_X/N_Y (doublon)
+ Adapter Regard.py à notre modèle
+ ~~Normaliser les données après transformations 128+noise+logpol~~
    + Réaliser le benchmarking des paramètres mean et std 
+ Corriger le calcul de la nouvelle position du stimulus avec saccade -> (max(a,b) - min(a,b)) ?
+ **Modifer la figure model.odg pour s'adapter aux notes manuscrites**
+ Intégrer la possibilité de créer les figures dans Where.py et réaliser un cleanup de LogPol_figures.ipynb pour ne faire qu'appeler ses fonctions

### Rapport de stage
+ ~~Ecrire une ébauche d'Introduction~~
+ ~~Ecrire une ébauche de Matériel et méthodes~~
+ **Ecrire une ébauche de Résultats**
+ Ecrire une ébauche de Discussion

---
# A lire
+ http://bethgelab.org/media/publications/Kuemmerer_High_Low_Level_Fixations_ICCV_2017.pdf
+ https://pdfs.semanticscholar.org/0182/5573781674bcf85d0f5d2ec456842f75ad3c.pdf
+ Schmidhuber, 1991 (voir mail Daucé)
+ Parr and Friston, 2017 (voir mail Perrinet)
+ http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003005#s1
+ http://rpg.ifi.uzh.ch/docs/RAL18_Loquercio.pdf
+ https://www.nature.com/articles/sdata2016126
+ [Liu et al., 2016](http://ieeexplore.ieee.org/document/7762165/?reload=true) : Learning to Predict Eye Fixations via Multiresolution Convolutional Neural Networks
+ [Papier utilisant une méthode similaire à la notre + intégration en robotique](https://www.researchgate.net/publication/220934961_Fast_Object_Detection_with_Foveated_Imaging_and_Virtual_Saccades_on_Resource_Limited_Robots)
+ Focal Loss for Dense Object Detection, Lin et al. 2017 (cf mail Hugo)
+ [Rosten et al., 2008](https://arxiv.org/abs/0810.2434) : Faster and better: a machine learning approach to corner detection
### Magnocellular pathway function  
+ [Selective suppression of the magnocellular visual pathway during saccadic eye movements](http://www.nature.com.lama.univ-amu.fr/articles/371511a0), Burr1994
+ [On Identifying Magnocellular and Parvocellular Responses on the Basis of Contrast-Response Functions](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3004196/), Skottun2011
+ [Review: Steady and pulsed pedestals, the how and why of post-receptoral pathway separation](http://jov.arvojournals.org/article.aspx?articleid=2191890), Pokorny2011
+ [An evolving view of duplex vision: separate but interacting cortical pathways for perception and action](http://www.sciencedirect.com/science/article/pii/S0959438804000340?via%3Dihub), Goodale2004
+ [Quantitative measurement of saccade amplitude, duration, and velocity](http://n.neurology.org/content/25/11/1065), Baloh1975
### Peripherical vision function
+ [The Role of Peripheral Vision in Configural Spatial Knowledge Acquisition](https://etd.ohiolink.edu/pg_10?0::NO:10:P10_ACCESSION_NUM:wright1496188017928082), Douglas2017

---
# Satellites
Des choses intéressantes qui gravitent autour de l'IA/ML et des neurosciences mais qui ne concernent pas directement notre sujet...