
% ****** An example of a submission to the first Technion Prediction Tournament *** 

%This example is an implementaion (using MATLAB) of the Cumulative Prospect Theory model 
% described in the competition web site.  This model was designed to predict the 
% results of Condition Description (decisions under risk).


%The current program has four parts.  The first three parts should be in all the submissions.

%Part 1 reads the input. 

%Part 2 derives the predictions of the model. The participants should express their ideas at 
%this parts.  They can use parts of the baseline models if they wish.

%Part 3 creates the output file.  Section 3 in the submissions should be be identical to part 3
%in the current example with the exception of the name of the output file.  
%Upon registration, the participant will  receive the name of their file.  The name will  
%include reference to the type of the competiton and the name of the participant.


%Part 4 will be added by the organizer of the competitions.

%Note: This example can be used as a first draft of a submission.  To try different models on the 
%estimation set you should replace the input file name.  Compar.dat should be replaced 
%with estpar.dat, and Comdat.dat should be replaced with estdat.dat.  The estimation files can be 
%downloaded from the competition site



%%%%***************  Part 1 Input*************************************************;
%it should appear as is in all the MATLAB submissions;

condition = 'desc'

%%-------------- parameters-----------------------
lam0=1;
alf=.86;	
lam1=1; 
gam=.5; 
lam2=1; 

load 'c:\compar.dat'; data = compar; 	%to use to evaluate models change to estpar.dat;

nt = 60;				            %number of problems

x = data(1:nt,[1 2 3 4 5]);      % Prob, high, Ph, low, med,  
pred=data(1:nt,[1]);
%%%% -------------------- PART 2   THE MODEL  and the derivation of the prediction  -----------------------------
 
msd=0;%initialize
v = [0;0]; %initialize
pros = [0;0];%initialize


%-----------------------------------MODEL-----------------------
% computing prospects for each  problem t
for t =1  :nt

    xt = x(t,:);    % current prospect; one row in x, for trial t
    
    % payoffs and probabilities for options  S and R
   
    
    high=xt(2);  ph=xt(3); low=xt(4);
    med=xt(5); Ps1=1;Ps2=1-Ps1; 
    Pr1=ph;Pr2=1-ph;

   
%----------------------   value  Function-----------------------------------
vs1 = med^alf; 
if med<0
    vs1 = -lam0*(abs(med^(alf*lam1)));
end

vr1 = high^alf;
if high<0
    vr1 = -lam0*(abs(high^(alf*lam1)));
end

vr2 = low^alf;
if low<0
    vr2 = -lam0*(abs(low^(alf*lam1)));
end


%----------------------------weighting  function----------------------------------------------;
   %if the gamble is mixed then there is no cumulative weighthing
   %lam2 is the parameter that determines whether there is different
   %weighting for probability of gains and losses
   gaml=gam*lam2; 
   
   if med>=0 
        fs1=(Ps1^gam) / (((Ps1^gam)+(1-Ps1)^gam)^(1/gam));
    else
        fs1=(Ps1^gaml) / (((Ps1^gaml)+(1-Ps1)^gaml)^(1/gaml));
   end

     if high>=0 
       fr1=(Pr1^gam)/(((Pr1^gam)+((1-Pr1)^gam))^(1/gam));
    else
        fr1=(Pr1^gaml)/(((Pr1^gaml)+((1-Pr1)^gaml))^(1/gaml));
     end

     if low>=0
        fr2=(Pr2^gam)/(((Pr2^gam)+((1-Pr2)^gam))^(1/gam));
    else
          fr2=(Pr2^gaml)/(((Pr2^gaml)+((1-Pr2)^gaml))^(1/gaml));
    end
    
  % computing cumulative if both outcomes are of the same sign

if sign(high)==sign(low) 
    if abs(high)>abs(low) 
        fr2=1-fr1;
    else
        fr1=1-fr2;
    end
end

pros(1)=fs1*vs1;
pros(2)=fr1*vr1+fr2*vr2;
 
if pros(1)>pros(2) 
    p= [1 0];
else
    p=[0 1];
end

   pp=p(2);
    pred (t)=  pp;
end


%%%% -----------------------------------------PART 3  The OUTPUT --------------------------
%it should appear with the new name (to be received by Email as is in all the 
%MATLAB submissions)

res = [x pred];

save out_example_risk.txt  res -ascii

%%%% ------------------   Part 4:  This part should not be part of the submission.  The organizers of 
%the competition will add it to compute the MSD    scores.------------

if condition=='desc'
    i=6
elseif condition=='samp'
    i=7
elseif condition=='feed'
    i=8
end
       comset=[res data(1:nt, i) ];
act=comset(1:nt,7);
       

sumd=0;
     msd= ones(60,1);
       msd=msd*1000;
      diff=pred-act;
      for i=1:nt
          di=diff(i);
          md=diff(i)^2;
          msd (i)=  md;
          sumd=sumd+md;
      end
comset=[comset msd]
mmsd=sumd/60;
mmsd=mmsd*100


