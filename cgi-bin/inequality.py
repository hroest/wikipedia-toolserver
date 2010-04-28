#! /usr/bin/env python
#
#
#GPL(c): Goetz Kluge, Munich 2004-09-17
#
#inequality.lua 1.4.0: inequality computations for welfare economics
#GPL(c): Goetz Kluge, Munich 2007-07-07
#Changes:
#  (1) symmetric inequality was Kullback-Leibler inequality
#  (2) Coulter Inequality:
#      inequality.Coulter = math.sqrt(sum.square/2)
#
#inequality-2.0.1.py is quite similar to inequality-2.0.1.lua (output looks a
#bit different) and is the core of http://www.poorcity.richcity.org/cgi-bin/inequality.cgi
#
#The "Societal aversion against inequality" (SOEP) is epsilon. I avoid
#using it, but the program ist prepared. Example for epsilon settings:
#    epsilon = 1:   undistorted data (I recommend that setting)
#    epsilon = 0.5: low aversion against inequality
#    epsilon = 2:   high aversion against inequality
#
#
# From http://luaforge.net/frs/?group_id=49

# initialization ----------------------------------------------------------

# use math library
import math


# define classes -----------------------------------------------------------

#---------------------------------------------------------------------------
class Object:
  def __init__(self):
    """ nothing to construct """
    pass
# def get(self,name):
#   """ makes getattr a method of this object """
#   return getattr(self,name)
# def set(self,name,value):
#   """ makes setattr a method of this object """
#   setattr(self,name,value)
  def prt(self,namelist):
    """ print selected elements of object """
    for name in namelist:
      print name+": %.3f" % getattr(self,name)
      
#---------------------------------------------------------------------------
class Redundancy(Object):
  def prt(self,namelist,epsilon):
    """ print selected elements of Redundancy """
    for name in namelist:
      print name.replace("_","-")+" redundancy: %.3f" % ((getattr(self,name)) * epsilon)
   
#---------------------------------------------------------------------------
class Equality(Object):
  def prt(self,namelist,epsilon):
    """ print selected elements of Equality """
    for name in namelist:
      print name.replace("_","-")+" equality: %.1f%%" % (((getattr(self,name)) ** epsilon)*100)
   
#---------------------------------------------------------------------------
class Inequality(Object):
  def prt(self,namelist,epsilon):
    """ print selected elements of Inequality """
    for name in namelist:
      print name.replace("_","-")+" inequality: %.1f%%" % ((1 - (1-getattr(self,name)) ** epsilon)*100)
   
#---------------------------------------------------------------------------
class Variation(Object):
  def prt(self,namelist):
    """ print selected elements of Variation """
    for name in namelist:
      print name.replace("_","-")+" variation: %.3f" % getattr(self,name)
   
#---------------------------------------------------------------------------
class Sum(Object):
  def prt(self,namelist):
    """ print selected elements of Sum """
    for name in namelist:
      print name.replace("_","-")+" total: %.3f" % getattr(self,name)
   


# define functions ---------------------------------------------------------

#---------------------------------------------------------------------------
def ineq(in_dataset):
  """ compute inequalities from a set of quantiles """
  absolute = Object()

  # add to quantile: ln(e[i]/a[i]) and i
  # (example: a people in a quantile together earn an income of e)
  dataset = []
  for q in in_dataset:
    quantile = Object() # new quantile
    quantile.a = (q[0] + 1E-66)
    quantile.e = (q[1] + 1E-66)
    quantile.log = math.log(quantile.e/quantile.a)
    quantile.oldi = len(dataset)  # we memorize the original sequence just in case...
    dataset.append(quantile)
  n = len(dataset)
  absolute.quantiles = n

  # sort table by ln(e[i]/a[i]) (only necessary for Gini)
  dataset.sort(
    lambda firstquantile,secondquantile:
      cmp(firstquantile.log,secondquantile.log)
  )

  # computations (Lorenz curve and growth)
  dataset[0].accua = dataset[0].a  # initialize accu a
  dataset[0].accue = dataset[0].e  # initialize accu e
  for i in range(len(dataset)-1):
    quantile = dataset[i+1]
    quantile.accua = dataset[i].accua + quantile.a  # x (could be used for Lorenz curve)
    quantile.accue = dataset[i].accue + quantile.e  # y (could be used for Lorenz curve)
    quantile.growth = math.exp(quantile.log - dataset[i].log)  # (experimental)
    dataset[i+1] = quantile

  # compute totals
  sum = Sum()
  sum.a = dataset[-1].accua
  sum.e = dataset[-1].accue
  sum.logxa = 0.
  sum.logxe = 0.
  sum.lorenz = 0.
  sum.abs = 0.
  sum.square = 0.
  sum.var = 0.
  for quantile in dataset: 
    sum.var += (quantile.e/quantile.a-sum.e/sum.a)**2 * quantile.a/sum.a
    x = abs(quantile.e/sum.e - quantile.a/sum.a)
    sum.abs +=  x
    sum.square += x*x
    sum.logxa += quantile.log * quantile.a
    sum.logxe += quantile.log * quantile.e
    sum.lorenz += (quantile.accue * 2 - quantile.e) * quantile.a

  # compute mean and median --
  absolute.mean = sum.e/sum.a
  halfpeople = sum.a/2
  last_qe = 0
  last_qa = 0
  people = 0
  imedian = 0
  for quantile in dataset:
     imedian += 1
     absolute.medianquantile = imedian
     absolute.median = (quantile.e + last_qe) / (quantile.a + last_qa)
     people += quantile.a
     if (people > halfpeople):
       break
     if ((absolute.quantiles % 2) == 0):
       last_qe = quantile.e
       last_qa = quantile.a

  # compute redundancies and inequalities
  # (actual "redundancy" is max. entropy minus actual entropy)
  equality = Equality()
  inequality = Inequality()
  redundancy = Redundancy()
  variation = Variation()
  x = math.log(sum.a) - math.log(sum.e)
  redundancy.Theil = sum.logxe/sum.e + x
  if (redundancy.Theil < 0):
    redundancy.Theil = 0
  redundancy.Theil_swapped = -sum.logxa/sum.a - x
  if (redundancy.Theil_swapped < 0):
    redundancy.Theil_swapped = 0
  redundancy.Symmetric= (redundancy.Theil + redundancy.Theil_swapped)/2
  equality.MacRae = math.exp(-redundancy.Theil)
  inequality.Atkinson = 1 - equality.MacRae
  inequality.Symmetric= 1 - math.exp(-redundancy.Symmetric)
  inequality.Hoover = sum.abs/2
  inequality.Gini = 1 - (sum.lorenz/sum.e)/sum.a
  equality.Europe = (1-inequality.Gini)/(1+inequality.Gini)
  inequality.Europe = 1 - equality.Europe
  # inequality.Herfindahl = sum.square  # not okay
  inequality.Coulter = math.sqrt(sum.square/2) # not decomposable
  variation.Williamson = math.sqrt(sum.var)*sum.a/sum.e

  # compute Platon inequality
  kli = inequality.Symmetric
  dkli = 1
  inequality.Platon = 1
  while ((abs(dkli)>0.00001) and (kli<1) and (kli>0)):
    pareto = math.asin((1-kli)**(kli*0.06+0.61))/math.pi
    dkli = 0
    if (pareto>0):
      inequality.Platon = 1-2*pareto  # e.g. (0.4+1)/2=0.7: 70% own 30%, 30% own 70%
      dkli = (1/pareto-1)**(-inequality.Platon) - 1 + inequality.Symmetric
      if (inequality.Platon > 0.97):
        dkli = dkli/10
    kli += dkli

  return inequality,redundancy,equality,variation,sum,absolute


#---------------------------------------------------------------------------
def printresults(container):
  inequality,redundancy,equality,variation,sum,absolute = container
  epsilon = 1   # keep epsilon = 1 for undistorted data
  #inequality.prt(("Symmetric","Atkinson","Gini","SOEP","Coulter","Hoover"),epsilon)
  inequality.prt(("Symmetric","Atkinson","Gini","Europe","Hoover"),epsilon)
  # equality.prt(("MacRae",),epsilon) # okay, but not so interesting
  # variation.prt(("Williamson",)) # okay, but not so interesting
  print ""
  redundancy.prt(("Symmetric","Theil"),epsilon) # okay, but not so interesting
  print ""
  s = "%d quantile elements" % sum.a
  print s
  s = "Mean:    %.3f per quantile element" % absolute.mean
  print s
  if (((absolute.quantiles % 2) == 0) and (absolute.medianquantile > 1)):
    x = (absolute.medianquantile - 1)
    s = "Median:  %.3f (#%d/%d and #%d/%d)" % (absolute.median,x,absolute.quantiles,absolute.medianquantile,absolute.quantiles)    
  else:
    s = "Median:  %.3f (#%d/%d)" % (absolute.median,absolute.medianquantile,absolute.quantiles)
  print s
  s = "Welfare: %.3f (using Gini)" % ((1 - inequality.Gini) * absolute.mean) 
  print s
  s = "Welfare: %.3f (using Atkinson)" % ((1 - inequality.Atkinson) * absolute.mean) 
  print s
  s = "Welfare: %.3f (using symm.)" % ((1 - inequality.Symmetric) * absolute.mean)
  print s
  return inequality

