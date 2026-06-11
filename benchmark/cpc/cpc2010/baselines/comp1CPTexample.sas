****** An example of a submission to the first Technion Prediction Tournament ***
This example is an implementaion (using SAS) of the cumulative prospect theory model 
described in the competition web site.  This model was designed to predict the 
results of Condition Description (decisions under risk).

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


data v; infile 'Compar.dat';  **to use to evaluate models change to estdat.dat ;
input problem  High ph low med;

*****************************Part 2 the derivation of the prediction******************;

data v; set v; 
Condition='risk'; del=1;
nsim=1;  **number of simlations;

***parameters********;
   do alfa=.88;
    do bet= 1;
     do gamag= .61;
	    do gal=1.132;*.5, .58, .6, .7, .8;
        do lambda= 2.25;*0.6, 0.8,1,1.25, 1.5,2,2.25;	 		
  output;
  end; end; end; end; end; 

  data v; set v; 
beta=alfa*bet;
gamal=gamag*gal;


array vv{2,2} va1 va2 vb1 vb2;
array ut{2,2} uta1 uta2 utb1 utb2;
array uu{2,2} ua1 ua2 ub1 ub2;
array pp{2,2} pa1 pa2 pb1 pb2;
array ff{2,2} fa1 fa2 fb1 fb2;
array wv{2} wv1 wv2;
array up{2} up1 up2;
array rel{2} rel1 rel2;

******assigning the file variables the pt variables;
va1=high;va2=low;
vb1=med;vb2=med;
pa1=ph;pa2=1-pa1; pb1=1;pb2=1-pb1;g=problem;

***new sim****************************;
if abs(va2)>abs(va1) then do; 
 tmp1=va1; tmp2=va2;
 va2=tmp1; va1=tmp2; pa1=1-pa1;
end;
if abs(vb2)>abs(vb1) then do; 
 tmp1=vb1; tmp2=vb2;
 vb2=tmp1; vb1=tmp2; pb1=1-pb1;
end;



pred=0;
do s=1 to nsim; 
alf=alfa;
lam=lambda;
gam=gamag;

****cpt value function****;
do g=1 to 2; do i=1 to 2;
ut{g,i}=ABS(1*vv{g,i})**alf;
if vv{g,i}<0 then ut{g,i}=-lam*abs(vv{g,i})**beta;
uu{g,i}=ut{g,i};

end; end;
*****weighting function*******;
do g=1 to 2;
 
gam=gamag; if vv{g,1}<0 then gam=gamal;
 ff{g,1}=del*(pp{g,1}**gam)/(((del*(pp{g,1}**gam)+((1-pp{g,1})**gam)))**(1/gam));
 ff{g,2}=1-ff{g,1};
 
if sign(vv{g,1})* sign(vv{g,2})<0 then do;

 if vv{g,1}>0 then do; 
ff{g,1}=del*(pp{g,1}**gamag)/(((del*(pp{g,1}**gamag)+((1-pp{g,1})**gamag)))**(1/gamag));
 qq=1-pp{g,1};
 ff{g,2}=del*(qq**gamal)/(((del*(qq**gamal)+((1-qq)**gamal)))**(1/gamal));
 end; **of 1 pos;

 if vv{g,1}<0 then do; 
 ff{g,1}=del*(pp{g,1}**gamal)/(((del*(pp{g,1}**gamal)+((1-pp{g,1})**gamal)))**(1/gamal));
 qq=1-pp{g,1};
 ff{g,2}=del*(qq**gamag)/(((del*(qq**gamag)+((1-qq)**gamag)))**(1/gamag));
 end; **of 1 neg;
 
end;

end;**of g;

*****integrating the values and weights****; 
do g=1 to 2;
wv{g}=ff{g,1}*uu{g,1}+ff{g,2}*uu{g,2};
end;**of g;

*** CPT precdition ******;
if wv{1}>wv{2} then pred=pred+1/nsim;
if wv{1}=wv{2} then pred=pred+0.5/nsim;




****P risk statistic********************;

risk=0; if dec=1 then risk=1;
pred=pred+risk/(nsim);

end; **of sim;

proc print; run; 


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


