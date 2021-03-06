 ## Sect Label with Bag of words encoder and random initial word embeddings  

SectLabel is aimed at performing logical section classification. 23 different classes are 
considered for classification. More information about SectLabel Classification 
can be obtained from [The Original paper](https://www.comp.nus.edu.sg/~kanmy/papers/ijdls-SectLabel.pdf)

This example shows how to perform Logical Section Classifier using SciWING.
A randomly initialized embedding is combined with ELMO embedding at the initial layer followed 
by a bidirectional lstm network and linear classifer. 

### Download the data 

``sciwing download data --task sectlabel``

Downloads the sectlabel data

## Writing your own python client to perform classification 
The file `sectlabel_elmo_bilstm.py` shows how to write the client file to run the classifier. 

To run training you can 
`sh sectlabel_elmo_bilstm.sh`

## Running from a toml file 
The experiment configuration can also be specified using a TOML file. Take a look 
at `sectlabel_elmo_bilstm.toml` file. 

#### To run training, validation and testing, run 

`sciwing run sectlabel_elmo_bilstm.toml`

#### To check results after running training using best model 

``sciwing test sectlabel_elmo_bilstm.toml``
` 

