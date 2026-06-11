****** An example of a submission for the first Technion Behavior Prediction Competion ***
This example is an implementaion (using SAS) of the normalized reinforcement learning model
described in the competition web site.  This model was designed to predict the results of 
Condition Experience repeated (feedback).

The current program has four parts.  The first three parts should be in all the submissions.

Part 1 reads the input. 

Part 2 derives the predictions of the model. The participants should express their ideas at 
this parts.  They can use parts of the baseline models if they wish.

Part 3 creates the output file.  Section 3 in the submissions should be be identical to part 3
in the current example with the exception of the name of the output file.  
Upon registration, the participant will  receive the name of their file.  The name will  
include reference to the type of the competiton and the name of the participant.

Part 4 will be added by the organizer of the competitions.

Note: This example can be used as a first draft of a submission.  To try different models on the 
estimation set you should replace the input file name.  Compar.dat should be replaced 
with estpar.dat, and Comdat.dat should be replaced with estdat.dat.  The estimation files can be 
downloaded from the competition site

;
**************************Part 1 Input*************************************************;
**** it should appear as is in all the SAS submissions;


options linesize=78 pagesize=999;
libname out '';


data v; infile 'compar.dat';  **to use to evaluate models change to estpar.dat;
input problem  High ph low med;

*****************************Part 2 the derivation of the prediction******************;

data v; set v; 
Condition='feed';
nsim=1000;  **number of simlations;
r=100;** number of trials;
norm='y';
***parameters********;
 w=.15; lamb=1.1;
 
data v; set v;
 array wv{2} wv1 wv2;
 

***new sim****************************;
vrand=.5*(high*ph+low*(1-ph))+.5*med;***expected payoff from random play;
pred=0;
do s=1 to nsim; 
 do alt=1 to 2;  wv{alt}=vrand; end;

prev=vrand;
D=lamb; ***The initial value of the normalization term;

******* the 100 trials ********************************************************;
do t=1 to r;

********************decisions ******************************************;
if norm='n' then d=1;
 prisk= 1/(1+exp((wv2-wv1)*lamb/D)); 

 dec=1; if ranuni(0)>prisk then dec=2;

**outcomes***;
 
 if dec=1 then do;
  vt=low; if ranuni(0)<ph then vt= high;
 end;
 if dec=2 then vt=med;

** updating D*****;
D=sum(D*t/(t+1),abs(vt-prev)/(t+1));
prev=vt;
*d=1;

***P risk statistic********************;
risk=0; if dec=1 then risk=1;
pred=pred+risk/(100*nsim);

******** adaptation**********************************************************************;
wv{dec}=(1-w)*wv{dec}+w*vt;

end; **of trials***;
end; **of sim;


*****Part 3 the output ****************************************************************;
**** it should appear with the new name (to be received by Email as is in all the 
SAS submissions.; 

data out.Example_Feed; set v;

proc sort; by problem  High ph low med;

*keep condition problem  High ph low med pred;

proc print round;

***********Part 4.  This part should not be part of the submission.  The organizers of 
the competition will add it to compute the MSD scores.;

data c; infile 'comdat.dat'; **to use to evaluate models change to estdat.dat compar;
input problem  High ph low med risk samp feed;

data test; merge out.Example_Feed c;
by problem  High ph low med;

data test; set test;
if condition='risk' then msd=(risk-pred)**2;
if condition='samp' then msd=(samp-pred)**2;
if condition='feed' then msd=(feed-pred)**2;

proc print round;
var condition problem  High ph low med d wv1 wv2 pred feed;

proc means; var msd;
run;



