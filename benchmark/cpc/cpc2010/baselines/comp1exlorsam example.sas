****** An example of a submission for the first Technion Prediction Competion ***
This example is an implementaion (using SAS) of the explorative sampler model with recency 
described in the competition web site.  This model was designed to predict the results of 
Condition feedback.

The current program has four parts.  The first three parts should appear in all the submissions.

Part 1 reads the input. 

Part 2 derives the predictions of the model. The participants should express their ideas at 
this parts.  They can use parts of the baseline models if they wish.

Part 3 creates the output file.  Section 3 in the submissions should be be identical to part 3
in the current example with the exception of the name of the output file.  
Upon registration, the participant will  receive the name of their file.  The name will  
include reference to the type of the competiton 
(risk, sampling or feedback) and the name of the participant.

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
nsim=100;  **number of simlations;
r=100;** number of trials
***parameters********;
rec=1; delta=.55; beta=.1; wfp=.3; kapa=4; eps=.12; 


 array his{2,100} his1-his200;
 array no{2} no1 no2;
 array tot{2} tot1 tot2;
 array ave{2} av1 av2;

***new sim****************************;
pred=0;
do s=1 to nsim; 
 do alt=1 to 2; no{alt}=0; ave{alt}=0; 
 do tt=1 to 100; his{alt,tt}=.; end;
end;

D=1; dec=1+round(ranuni(0));
vt=0;

******* the 100 trials ********************************************************;
do t=1 to r;

********************decisions ******************************************;
pexp=(eps)**((t-1)/(t+r**delta)); ***probability of exploration***;
explor=0; if ranuni(0)<pexp then explor=1;

***explore************************************ ;
 if  explor=1 then do;
  dec=1; if ranuni(0)<.5 then dec=2; **symmetric exploration;
 end;


***exploit**************************************;
if explor=0 then do;
alfa=(1+D)**(-beta); ******* diminishing sensitivity term;
ncas=round(.5+ranuni(0)*kapa*2); **** sample size***;

do alt=1 to 2; tot{alt}=0;
 do i=1 to ncas; **sampling**;
    case=round(.5+no{alt}*ranuni(0));
	draw=his{alt,case};
    if rec=1 and i=1 then draw=his{alt,no{alt}};
    mem=(1-wfp)*draw+wfp*ave{alt};  
    if mem>=0 then smem=mem**alfa;
    if mem<0 then smem=-((-mem)**alfa);
    tot{alt}=sum(tot{alt},smem);
 end;
end;

dec=1; if tot2>tot1 then dec=2; if tot1=tot2 then dec=1+round(ranuni(0));**choice;

end; **of exploit;


**outcomes***;
 prev=vt;
 if dec=1 then do;
  vt=low; if ranuni(0)<ph then vt= high;
 end;
 if dec=2 then vt=med;

** updating D*****;
D=sum(d*t/(t+1),abs(vt-prev)/(t+1));

****P risk statistic********************;

risk=0; if dec=1 then risk=1;
pred=pred+risk/(100*nsim);
******** history**********************************************************************;

no{dec}=No{dec}+1;
his{dec,no{dec}}=vt;
ww=(no{dec}-1)/no{dec};
ave{dec}=ave{dec}*ww+vt*(1-ww);

if t=1 then do;
ndec=3-dec;
no{ndec}=1;
his{ndec,1}=vt;
ave{ndec}=vt;
end;


end; **of trials***;
end; **of sim;


*****Part 3 the output ****************************************************************;
**** it should appear with the new name (to be received by Email as is in all the 
SAS submissions.; 

data out.Example_Feed; set v;
keep condition problem  High ph low med pred;



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

proc means; 
var msd;
run;


