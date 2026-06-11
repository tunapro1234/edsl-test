****** An example of a submission to the first Technion Prediction Tournament ***
This example is an implementaion (using SAS) of the primed sampler model with individual 
differences described in the competition web site.  This model was designed to predict the 
results of Condition sampling.

The current program has 4 parts.The first 3 parts should be in all the submissions.

Part 1 reads the input. 

Part 2 derives the predictions of the model. The participants should express their ideas
in this parts.  They can use parts of the baseline models if they wish.

Part 3 creates the output file.  Section 3 in the submissions should be be identical to 
part 3 in the current example with the exception of the name of the output file.  
Upon registration, the participants will  receive the name of their file.  The name will  
include reference to the type of the competiton (risk, sampling or feedback) 
and the name/number of the competitor.

Part 4 will be added by the organizers of the competitions.

Note: This example can be used as a first draft of a submission.  To try different models 
on the estimation set you should replace the input file name.  Compar.dat should be 
replaced with estpar.dat, and Comdat.dat should be replaced with est.dat
The estimation files can be downloaded from the competition site

;
**************************Part 1 Input*************************************************;
**** it should appear as is in all the SAS submissions.;


options linesize=78 pagesize=999;
libname out '';


data v; infile 'compar.dat';  **to use to evaluate models change to estpar.dat compar;
input problem  High ph low med;

*****************************Part 2 the derivation of the prediction******************;

data v; set v; 
Condition='samp';
nsim=20000;  **number of simlations;

***parameters********;
kapa=9;  

 array tot{2} tot1 tot2;

***new sim****************************;
pred=0;
do s=1 to nsim; 

ncas=round(.5+ranuni(0)*kapa); **** sample size***;


do alt=1 to 2; tot{alt}=0;
 do i=1 to ncas; **sampling**;
  if alt=1 then do;
   vt=low; if ranuni(0)<ph then vt= high;
  end;
  if alt=2 then vt=med;
  tot{alt}=tot{alt}+vt;
 end;
end;
dec=1; if tot2>tot1 then dec=2; if tot1=tot2 then dec=1+round(ranuni(0));**choice;

****P risk statistic********************;

risk=0; if dec=1 then risk=1;
pred=pred+risk/(nsim);

end; **of sim;


*****Part 3 the output ****************************************************************;
**** it should appear with the new name (to be received by Email as is in all the 
SAS submissions.; 

data out.Example_samp; set v;
keep condition problem  High ph low med pred;



***********Part 4.  This part should not be part of the submission.  The organizers of 
the competition will add it to compute the MSD scores.;

data c; infile 'comdat.dat'; **to use to evaluate models change to estdat.dat compar;
input problem  High ph low med risk samp feed;


data test; merge out.Example_samp c;
by problem  High ph low med;


data test; set test;
if condition='risk' then msd=(risk-pred)**2;
if condition='samp' then msd=(samp-pred)**2;
if condition='feed' then msd=(feed-pred)**2;

proc print round;
proc corr; var samp feed pred msd;
proc means; 
var msd;

run;


