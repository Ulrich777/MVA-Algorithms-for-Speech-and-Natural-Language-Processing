# MVA-Algorithms-for-Speech-and-Natural-Language-Processing-TP2

To launch our parser tool, just run the script run.sh. He takes six compulsory
inputs

- Input 1: the path to sentences to parse
- Input 2: the path where to save the output
- Input 3: the smoothing parameter to Levenshtein distabce
- Input 4: the weighting parameter of similarityu metrics
- Input 5: the lowest line to process
- Input 6: the highest line to process

Therefore to process all the sentences in the evaluation dataset, you should 
set Input 5 and 6 respectively to 0 and 309.

A sample code to run it on windows:
bash run.sh C:\Users\utilisateur\Documents\GITHUB\TP2\code\sents_test.txt C:\Users\utilisateur\Documents\GITHUB\TP2\code\my_output.txt 0.3 0.3 304 308

For instance for the line: 'Lors_de ces échanges , Moggi donnait ses instructions pour la désignation des arbitres dans le
matches de son équipe' we will get the following output:
-->  '( (SENT (P Lors_de) (DET ces) (NC échanges) (PONCT ,) (NPP Moggi) (V donnait) (DET
ses) (NC instructions) (P pour) (DET la) (NC désignation) (P+D des) (NC arbitres) (P dans) (DET le)
(NC matches) (P de) (DET son) (NC équipe) (PONCT .)))' 
 
