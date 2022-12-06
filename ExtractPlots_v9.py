#!/usr/local/bin/python3

# VERSION Track: 
# this is _v8 which is prepared to save for Matlab, based on the new BCM1F Gemetry and the New FBCM2022
# _v7 which was prepared to save for Matlab, based on the new Gemetry and the last run for TDR 
# _7 was based on "ExtractPlots_v5", and "nZerosV0" was added to this version.
# this file is newer than "ExtractPlots_v5", but lacks the Root fitting in _v6 (which is based on root fitting)
# one should merge the changes of _v6 (modified by H.Bakhshian) to this file. 
from __future__ import print_function
import ROOT
#from scipy import stats
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from array import array
from ROOT import TCanvas, TGraph, TMath
import time
import os 
import sys
import argparse 
import math
import copy
from scipy import stats

import matplotlib.pyplot as plt
# import matplotlib.pyplot as plt
# from matplotlib.colors import BoundaryNorm
# from matplotlib.ticker import MaxNLocator
import numpy as np
import scipy.io as sio

NumOfBxInMixing = 7.0 # -3:3, i.e. 

def GetData1D(hst , rebinX): # rebi
    nX : intiger
    hst.Rebin(rebinX) # def rebinX=1 for get the orginal hist, rebinX>1 combines the bins
    nBins = hst.GetNbinsX()
    xAxis = hst.GetXaxis()
    yVect = np.zeros(nBins)
    xVect = np.zeros(nBins)
    for b in range( nBins ) :
        val = hst.GetBinContent(b+1)
        p = xAxis.GetBinCenter(b+1)
        yVect[b] = val
        xVect[b] = p
    #Data = np.vstack((xVect_np2, yVect_np2))    
    Data={"xAxis":xVect.astype('double'),"data":yVect.astype('double')}
    return Data
    
def GetData2D(hst , rebinX, rebinY): # rebinX,Y : intiger
    hst.Rebin2D(rebinX,rebinY) # def rebinX=1 for get the orginal hist, rebinX>1 combines the bins
    nBinsX = hst.GetNbinsX()
    nBinsY = hst.GetNbinsY()
    xAxis = hst.GetXaxis()
    yAxis = hst.GetYaxis()
    xVect = np.zeros(nBinsX)
    yVect = np.zeros(nBinsY)
    zVect = np.zeros((nBinsX,nBinsY))
    
    for xi in range( nBinsX ) :
        for yi in range(nBinsY) :
            b = hst.GetBin (xi,yi) 
            val = hst.GetBinContent(b+1)
            px = xAxis.GetBinCenter(xi+1)
            py = yAxis.GetBinCenter(yi+1)
            xVect[xi] = px
            yVect[yi] = py
            zVect[xi][yi] = val
    Data={"xAxis":xVect.astype('double'),"yAxis":yVect.astype('double'),"data":zVect.astype('double')}
    return Data
    

    

class SensorGroupInformation:
    def CopyH1IToH1F(self , h ):
        hret = ROOT.TH1F()
        h.Copy( hret )
        return hret

    def __init__(self , sensorGroup , pu , fIn , destDirectory):
        self.SensorGroup = sensorGroup
        self.PU = pu
        self.destDir = destDirectory
        self.InDir = fIn.GetDirectory( 'SensorGroup{0}'.format( self.SensorGroup ) )
        
        self.hnDigiBxSlots = self.InDir.Get("h{0}_SG{1}".format( 'numOfBxSlots' , self.SensorGroup ) )
        self.nBxSlotsInDigi = 5. #(self.hnDigiBxSlots.GetBinContent(1)) # GetData1D(self.hnDigiBxSlots , 1)
        #print("NumofBx slots is {0}".format(self.nBxSlotsInDigi))OB        #input("Number of BxSlots")
        
        self.nSimHits = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nSimHits' , self.SensorGroup ) ) )
        self.nDigiHits = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nDigiHits' , self.SensorGroup ) ) )
        self.nDigiHitsV2 = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nDigiHitsV2' , self.SensorGroup ) ) )
        self.nOnes = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nOnes' , self.SensorGroup ) ) )
        self.nUnknowns = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nUnknowns' , self.SensorGroup ) ) )
        self.nTotals = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'TotalNumbers' , self.SensorGroup ) ) ) 
        print( self.nTotals )

        
        self.nTotalRhuHitsPerBx = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nTotalRhuHitsPerBx' , self.SensorGroup ) ) ) 
        self.nInterstedBinRhuHits = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nInterstedBinRhuHits' , self.SensorGroup ) ) ) 
        self.nOnesAtRhuBin = self.CopyH1IToH1F( self.InDir.Get( 'h{0}_SG{1}'.format( 'nOnesAtRhuBin' , self.SensorGroup ) ) ) 
        
        
        
        self.TotRho = self.InDir.Get( 'h{0}_SG{1}'.format( 'TotRho' , self.SensorGroup ) )
        self.ToaRho = self.InDir.Get( 'h{0}_SG{1}'.format( 'ToaRho' , self.SensorGroup ) )
        self.TofRho = self.InDir.Get( 'h{0}_SG{1}'.format( 'TofRho' , self.SensorGroup ) )
        self.BxTofRho = self.InDir.Get( 'h{0}_SG{1}'.format( 'BxTofRho' , self.SensorGroup ) ) 
        
        self.RhuRho = self.InDir.Get( 'h{0}_SG{1}'.format( 'RhuRho' , self.SensorGroup ) )
        self.PeakAmpl = self.InDir.Get( 'h{0}_SG{1}'.format( 'PeakAmplitude' , self.SensorGroup ) )
        self.SumCharge = self.InDir.Get( 'h{0}_SG{1}'.format( 'SumCharge' , self.SensorGroup ) )

        #self.nTotals.Scale( self.nBxSlotsInDigi ) # x3 in early version 
        self.nSimHits.Divide( self.nTotals )
        self.nSimHits.Scale( 1.0/NumOfBxInMixing )
        
        self.nTotals.Scale( self.nBxSlotsInDigi ) # x3 in early version 
        
        self.nUnknownsRatio = self.nUnknowns.Clone("nUnknownsRatio_SG{0}".format(self.SensorGroup))
        self.nUnknownsRatio.Divide( self.nTotals )
        
        self.nDigiHits.Divide( self.nTotals )
        self.nTotalsMinusUnknowns = self.nTotals.Clone("nTotalsMinusUnknowns_SG{0}".format(self.SensorGroup))
        self.nZeros = self.nTotals.Clone("nZeros_SG{0}_PU{0}".format(self.SensorGroup , self.PU)) 
        self.nZeros.Add( self.nOnes , -1.0 ) 
        self.nZeros.Print()

        
        self.nZerosV0 = self.nZeros.Clone("nZerosV0_SG{0}".format(self.SensorGroup)) 
        
        self.nZeros.Add( self.nUnknowns , -1.0 )
        self.nTotalsMinusUnknowns.Add( self.nUnknowns , -1.0 )
        self.nZeros.Divide( self.nTotalsMinusUnknowns )
        self.nDigiHitsV2.Divide(self.nTotalsMinusUnknowns)
        for b in range( self.nZeros.GetNbinsX() ) :
            bc = self.nZeros.GetBinContent(b+1)
            if bc > 0:
                self.nZeros.SetBinContent( b + 1 , -math.log( bc ) )

        self.nZerosV0.Divide( self.nTotals )
        for b in range( self.nZerosV0.GetNbinsX() ) :
            bc = self.nZerosV0.GetBinContent(b+1)
            if bc > 0:
                self.nZerosV0.SetBinContent( b + 1 , -math.log( bc ) )
                
        self.rhuTimingEfficiency = self.nInterstedBinRhuHits.Clone("rhuTimingEfficiency_SG{0}".format(self.SensorGroup))
        self.rhuTimingEfficiency.Divide( self.nTotalRhuHitsPerBx )
        
        #self.nTotalRhuHitsPerBx.Scale( self.nBxSlotsInDigi )
        
        self.nRhuZeors = self.nTotals.Clone("nRhuZeors_SG{0}".format(self.SensorGroup)) 
        self.nRhuZeors.Add( self.nOnesAtRhuBin , -1.0 ) 
        
        self.lambdaDigiZC_Rhu = self.nRhuZeors.Clone("lambdaDigiZCntRhu_SG{0}".format(self.SensorGroup)) 
        self.lambdaDigiZC_Rhu.Divide( self.nTotals )
        for b in range( self.lambdaDigiZC_Rhu.GetNbinsX() ) :
            bc = self.lambdaDigiZC_Rhu.GetBinContent(b+1)
            if bc > 0:
                self.lambdaDigiZC_Rhu.SetBinContent( b + 1 , -math.log( bc ) )
        
        
        self.lambdaDigiC_Rhu  =  self.nInterstedBinRhuHits.Clone("lambdaDigiCntRhu_SG{0}".format(self.SensorGroup))
        self.lambdaDigiC_Rhu.Divide( self.nTotals ) 



    def Write(self,instancenname ):
        self.c1 = ROOT.TCanvas('cPU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        self.insn = instancenname 
        self.nZeros.SetLineColor( 3 )
        self.nZeros.SetTitle( '<Digi>-ZeroCounting' )
        self.nZeros.SetStats( False )
        self.nZeros.Draw(  )

        self.nDigiHits.SetLineColor( 2 )
        self.nDigiHits.SetTitle( '<Digi>-counting' )
        self.nDigiHits.SetStats(False)
        self.nDigiHits.Draw('same')

        self.nSimHits.SetLineColor( 4 )
        self.nSimHits.SetTitle('<sim-hits>')
        self.nSimHits.SetStats(False)
        self.nSimHits.Draw("SAME")

        self.c1.BuildLegend()
        self.c1.SaveAs( self.destDir + 'Myresult' +'_{0}_{1}.png'.format(self.insn, self.c1.GetName() ) )
        
    def hZeroCounting(self ):
        return self.nZeros
        
    def hZeroV0Counting(self ):
        return self.nZerosV0 

    def hCounting(self ):
        return self.nDigiHits
    
    def hCountingV2(self ):
        return self.nDigiHitsV2
        
    def hSimHits(self ):
        return self.nSimHits
    
    def hUnknownRatio(self ):
        return self.nUnknownsRatio
        
    def hOnes(self ):
        return self.nOnes

    def hUnknowns(self ):
        return self.nUnknowns

    def hNtotal(self ):
        return self.nTotals

    def hNTotalsMinusUnknowns(self ):
        return self.nTotalsMinusUnknowns        

    def hToaRho(self ):
        return self.ToaRho

    def hTotRho(self ):
        return self.TotRho

    def hTofRho(self ):
        return self.TofRho        
        
    def hBxTofRho(self ):
        return self.BxTofRho

    #
    def hPeakAmpl(self ):
        return self.PeakAmpl 
    
    def hSumCharge(self ):
        return self.SumCharge             
    
    def hRhuRho(self ):
        return self.RhuRho        
        
    def hNTotalRhuHitsPerBx(self ):
        return self.nTotalRhuHitsPerBx        

    def hNInterstedBinRhuHits(self ):
        return self.nInterstedBinRhuHits        
            
    def hRhuTimingEfficiency(self ):
        return self.rhuTimingEfficiency        
            
    def hNrhuZeors(self ):
        return self.nRhuZeors        

    def hLambdaDigiZCntRhu(self ):
        return self.lambdaDigiZC_Rhu        

    def hLambdaDigiCntRhu(self ):
        return self.lambdaDigiC_Rhu        
    #
    
    def WriteBxTof(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('Tof_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        y_proj = self.BxTofRho.ProjectionY("py",b)
        y_proj.SetName(self.BxTofRho.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        BxTof_1FH = ROOT.TH1F()
        y_proj.Copy(BxTof_1FH)
        BxTof_1FH.SetTitle( 'Tof' )
        BxTof_1FH.SetStats( False )
        BxTof_1FH.Rebin(2)
        BxTof_1FH.GetXaxis().SetRangeUser(-0.,25.0)
        BxTof_1FH.Draw()
        self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
        
    def WriteToA(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('ToA_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        y_proj = self.ToaRho.ProjectionY("py",b)
        y_proj.SetName(self.ToaRho.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        ToA_1FH = ROOT.TH1F()
        y_proj.Copy(ToA_1FH)
        ToA_1FH.SetTitle( 'ToA' )
        ToA_1FH.SetStats( False )
        ToA_1FH.Rebin(2)
        ToA_1FH.GetXaxis().SetRangeUser(-15.,15.)
        ToA_1FH.Draw()
        self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
        
    def WriteToT(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('ToT_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        y_proj = self.TotRho.ProjectionY("py",b)
        y_proj.SetName(self.TotRho.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        ToT_1FH = ROOT.TH1F()
        y_proj.Copy(ToT_1FH)
        ToT_1FH.SetTitle( 'ToT' )
        ToT_1FH.SetStats( False )
        ToT_1FH.Rebin(2)
        ToT_1FH.GetXaxis().SetRangeUser(-5.,31.)
        ToT_1FH.Draw()
        self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
        
    def WriteAmpl(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('Amplitude_mV_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        # print(b)
        y_proj = self.PeakAmpl.ProjectionY("py",b)
        y_proj.SetName(self.PeakAmpl.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        Ampl_1FH = ROOT.TH1F()
        y_proj.Copy(Ampl_1FH)
        # Ampl_1FH.Fit("TMath::Landau(-x)") # not works
        Ampl_1FH.SetTitle( 'Ampl(mV)' )
        Ampl_1FH.SetStats( True )
        Ampl_1FH.Rebin(1)
        # Ampl_1FH.GetXaxis().SetRangeUser(0.0,00.0)
        Ampl_1FH.Draw()
        #self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
    
    def WriteSimCharge(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('SumCharge_sim_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        # print(b)
        y_proj = self.SumCharge.ProjectionY("py",b)
        y_proj.SetName(self.SumCharge.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        Charge_1FH = ROOT.TH1F()
        y_proj.Copy(Charge_1FH)
        # Charge_1FH.Fit("TMath::Landau(-x)") # not works
        Charge_1FH.SetTitle( 'sum of collected charges' )
        Charge_1FH.SetStats( True )
        Charge_1FH.Rebin(7)
        # Charge_1FH.GetXaxis().SetRangeUser(0.0,00.0)
        Charge_1FH.Draw()
        #self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
        
    def WriteRhu(self, Rho, scanName):
        self.c2 = ROOT.TCanvas('Rhu_PU{0}SG{1}'.format( self.PU , self.SensorGroup ), 'PU{0}SG{1}'.format( self.PU , self.SensorGroup ) )
        #Tpadd=ROOT.TPad("H1","H2",)
        b = self.nSimHits.FindBin(Rho)
        y_proj = self.RhuRho.ProjectionY("py",b)
        y_proj.SetName(self.RhuRho.GetName()+"_projY{0}".format(self.SensorGroup))
        y_proj.Draw("same, hist")
        Rhu_1FH = ROOT.TH1F()
        y_proj.Copy(Rhu_1FH)
        Rhu_1FH.SetTitle( 'Rhu' )
        Rhu_1FH.SetStats( False )
        Rhu_1FH.Rebin(1)
        Rhu_1FH.GetXaxis().SetRangeUser(-6,6)
        Rhu_1FH.Draw()
        self.c2.BuildLegend()
        self.c2.SaveAs( self.destDir+'{0}_{1}.png'.format( self.c2.GetName(), scanName ) )
        
        
def puValue(x):
    return {
        '0' : 0.,
        '0p5': 0.5,
        '1': 1.,
        '1p5': 1.5,
        '2': 2.,
        '10': 10.,
        '30': 30.,
        '50': 50.,
        '100': 100.,
        '140': 140.,
        '200': 200.,
    }.get(x, -1.)  
          
            
def puCase(x):
    return {
        '0' : '/histBibSelfMixOut_pu',
        '0p5': '/outPU',
        '1': '/outPU',
        '1p5': '/outPU',
        '2' :  '/outPU',
        '10': '/outPU',
        '30': 'outPU',
        '50': '/outPU',
        '100': '/outPU',
        '140': '/outPU',
        '200': '/outPU',
    }.get(x, '/outPU')    
    
 
def getSrcDir(x,ver):
    return {
        'no_aging' : './resultsFbcm'+ver+'/no_aging/aging0_pu',
        'aging_1000': './resultsFbcm'+ver+'/aging_1000/aging1k_pu',
        'aging_3000': './resultsFbcm'+ver+'/aging_3000/aging3k_pu',
        'aging_4000': './resultsFbcm'+ver+'/aging_4000/aging4k_pu',
        'bib_selfMix': '/afs/cern.ch/work/m/msedghi/public/BeamInducedBackgrdFbcm/bibDIGI_SelfMixed/nTuplizerOutput/histResults',
        'bib_noMix': '/afs/cern.ch/work/m/msedghi/public/BeamInducedBackgrdFbcm/bibDIGI_NoMix/nTuplizerOutput/histResults' ,
        'bib_puMix': '/afs/cern.ch/work/m/msedghi/public/BeamInducedBackgrdFbcm/bibDIGI_PileupBibMixed/nTuplizerOutput/histResults',
    }.get(x, '/outPU')  

    
def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument( '-i' , '--infile' , dest='infile' , help='the name of the input file' , type=str  )
    parser.add_argument( '-s' , '--src' , dest='srcDir' ,default='.', help='the name of the source base directory' , type=str  )
    #parser.add_argument( '-p' , '--pu' , dest='PU' , default=None , help='the pu of the file' , type=str , choices=['0p5','1','1p5', '2', '10' , '30' , '50', '100' ,'140', '200', 'all'])

    parser.add_argument( '-t' , '--srcType' , dest='srcType' , default=None , help='the source type' , type=str , choices=['no_aging', 'aging_1000', 'aging_3000' , 'aging_4000' , 'bib_selfMix' , 'bib_noMix' , 'bib_puMix'])
    parser.add_argument( '-v' , '--ver' , dest='srcVer' , default='V2' , help='the source Version directory' , type=str , choices=['V1', 'V2'])
    
    opt = parser.parse_args()
    
    ExplicitInputfile = False
    
    if opt.infile:
        ExplicitInputfile = True
        if opt.infile[0]=='.' :
            destDir="/".join(opt.infile.split(os.sep)[0:-2])+'/'
            baseInFileName = (opt.infile.split(os.sep)[-1]).split('.')[0]
            
        elif opt.infile[0]!='/':
            destDir="."+"/".join(opt.infile.split(os.sep)[0:-2])+'/'
            baseInFileName = opt.infile.split('.')[0]
        else:
            destDir="/".join(opt.infile.split(os.sep)[0:-2])+'/'
            baseInFileName=(opt.infile.split(os.sep)[-1]).split('.')[0]
        
        #instanceName = baseInFileName.split('_')[1]
        
        # print(instanceName)
        opt.srcType = instanceName
        print("dest Dir is {0}".format(destDir))
        #input("destdir stop")
        # exit(0)
        #return
    elif opt.srcDir:
        opt_srcDir=opt.srcDir+'/'
        print("opt_srcDir=",opt_srcDir)
        input("stop for opt_srcDir")
        infile=next(os.walk(opt_srcDir), (None, None, []))[2]  # [] if no file
        print("files=",infile)
        input("stop for files")
        #print(destDir)
        
    

    
#    if not opt.PU:
#        print('please specify the pu using -p option')
#        return 1
    
#    if opt.PU=='all':
#        opt.PU = ['0p5','1','1p5', '2' , '10' , '30' , '50' ,'100','140', '200' ]
#    else :
#        opt.PU =[opt.PU]
    
    
    ROOT.gStyle.SetOptTitle(0)
    
    #puDict = dict.fromkeys(opt.PU, list())
    
    instancenames = ['Vtsh30mV','Vtsh60mV','Vtsh90mV','Vtsh120mV']
    mylist=[]
    for insn in instancenames:
        puDict = {}
        i = 0
        
        for file in infile:
            sg_list = {}
            #nstanceName = file.split("_")[1]
            #print("instanceName=",instancenames)
            pu = file.split("_")[2].split(".")[0].split("pu")[1]
            print("pu = ",pu)
            if pu == '0p5':
                pu = '0.5'
            elif pu == '1p5':
                pu = '1.5'
            #print("pu=",pu)
            #input("stop for pu")
            if insn in file:
                i += 1
                
                fIn = ROOT.TFile.Open( 'results/'+file )    
                #print("file=",file,'\n',"instzncename=",insn)
                #input("test{}".format(pu))
                hnSensorGroups = fIn.Get("hnSensorGroups")
                nSensorGroups = 1 #int(hnSensorGroups.GetBinContent(1))
                #print("i=",i)
                #print("number of Sensor groups is {0}".format(nSensorGroups))
                #sg_list=list()
                
                destDir="."+"/".join(file.split(os.sep)[0:-2])+'/'
                #print("detdir=",destDir)
                #input("destdir=")
                sg = '0'
                s = SensorGroupInformation(sg , pu , fIn , destDir)
                #print("pu=",pu)
                sg_list[pu] = copy.deepcopy(s)
                #print("sg_list=",sg_list)
                puDict[pu+"_"+insn] = sg_list
                #print("pudict=",puDict)
        #puDict[pu+"_"+ insn].append( sg_list)        
        #print("pudict=",puDict)
        #input("end od file loop")        
        
        print("i is ",i)
        
        mylist.append(puDict)        
    #print("mylist=",len(mylist))            
    #input("stop ooooooo")
     # print("------------")
     # puVect = {
    Rho = np.linspace(9.,21.,25)
    chidict={}
    for rho in Rho:
        #print("rho=",rho)
        #input("stop for rho")
        for i  in range (len(mylist)):
            dict = {}
            x=[]
            x1, y1_Sim ,y1_Digi= array( 'd' ), array( 'd' ), array( 'd' )
            x2, y2_Sim, y2_Digi = array( 'd' ), array( 'd' ), array( 'd' )
            N , yerrsim , yerrdigi, xerr = array( 'd' ), array( 'd' ),array( 'd' ),array('d')
            ydigi=[]
            ysim=[]
            yzero=[]
            #puVal=puValue(pu)
            #puVect[opt.PU.index(pu)] = puVal
            print("\n\n\n mylist[{}]".format(i)+"=",mylist[i].keys())
            #input("test1")
            for key in mylist[i].keys():
                #print("\n",key)
                #input("test")
                insn = key.split("_")[1]
                #sortedkey2 = mylist[i][key].keys()
                #print("sortedkey2=",sortedkey2)
                #input("stop for sortedkey")
                for key2 in mylist[i][key].keys():
                    #print("key2=",key2,"key2.split=",key2.split("_"))
                    pu = key2
                    print("pu=",pu,"\n","insn=",insn)


           #print("pu=",pu,'\n',"puval=",puVal,'\n',"sg=",sg,'\n',"destDir=",destDir,'\n',"type puDict=",type(puDict))
           #input("stop please")
           #print("puDict new=",type(puDict[pu][0].hZeroCounting()))
           #input("checkpoint")
                    mylist[i][key][key2].Write(insn)
                    nDigiHits = GetData1D( mylist[i][key][key2].hCounting() , 1 )
                    nZeros = GetData1D( mylist[i][key][key2].hZeroCounting() , 1 )
                    nSimHits = GetData1D( mylist[i][key][key2].hSimHits() , 1 )
                    Ntot = GetData1D( mylist[i][key][key2].hNtotal() , 1 )
                    
                    print("nTolal=",Ntot)
                    #input("stop for Ntotal")
                    index = np.where(nZeros['xAxis']==rho)[0][0]
                    index1 = np.where(nSimHits['xAxis']==14.5)[0][0]
                    #dict[pu] = nZeros_data['data'][index]
                    #print(dict)
                    #input("stop for dict")
                    N = Ntot['data'][index]
                    x1.append(float(pu))
                    y1_Sim.append(nSimHits['data'][index])
                    y1_Digi.append(nDigiHits['data'][index])          
                    x.append(float(pu))
                    xerr.append(0.)
                    #simerr = nSimHits['data'][index]
                    #digierr = nDigiHits['data'][index]
                    ysim.append(nSimHits['data'][index])
                    ###########################################################
                    #  Getting Errors                                         #
                    ###########################################################
                    
                    
                    
                    yerrsim.append(math.sqrt(nSimHits['data'][index]/N))
                    #yerrsim.append(0.04)
                    #yerrdigi.append(0.04)
                    yerrdigi.append(math.sqrt(nDigiHits['data'][index]/N))
                    ydigi.append(nDigiHits['data'][index])
                    yzero.append(nZeros['data'][index])
                    #print("x=",x,"y=",y)
                    ###########################################################
            print("x1 = ",x1,"\n","y1 = ",y1_Sim)

            #input("Stop nZeros_Data")
            arrx = np.array(x)
            arry = np.array(ydigi)
            

            #plt.plot(x, ydigi,'o', c ="blue")
            #gradientDigi, interceptDigi, r_valueDigi, p_valueDigi, slope_std_errorDigi = stats.linregress(x[0:3], ydigi[0:3])
            #gradientSim, interceptSim, r_valueSim, p_valueSim, slope_std_errorSim = stats.linregress(x[0:3], ysim[0:3])
            #gradientZero, interceptZero, r_valueZero, p_valueZero, slope_std_errorZero = stats.linregress(x[0:3], yzero[0:3])
            #linearDigi = stats.linregress(x[0:3], ydigi[0:3]) 
            #predictDigi_y = [gradientDigi * i + interceptDigi for i in x]
            #predictSim_y = [gradientSim * i + interceptSim for i in x] 
            #predictZero_y = [gradientZero * i + interceptZero for i in x]
            c1 = TCanvas( 'c1', 'A Simple Graph Example', 600,400 )
            #c2 = TCanvas( 'c2', 'A Simple Graph Example', 200, 10, 700, 500 )
            ROOT.gStyle.SetOptStat(1)
            ROOT.gStyle.SetOptFit(1)
            #x2, y2 = zip(*sorted(zip(x1, y1)))
            #x2 = [float(m) form in x2]
            #y2 = [float(m) for m in y2]
            
            for s in x1:
                if s <10:
                    x2.append(s)
                    y2_Sim.append(y1_Sim[x1.index(s)])
                    y2_Digi.append(y1_Digi[x1.index(s)])
            print("x2 = ",x2,"\n","y2 = ",y2_Sim)
            ###################################################################
            #   Plots for Sim                                                 #
            ###################################################################

            gfitSim = ROOT.TGraphErrors(4,x2,y2_Sim,xerr,yerrsim)
            gfitSim.SetName("gfitSim")
            gfitSim.GetXaxis().SetLimits(0.,205.)
            #gfitSim.SetMarkerStyle(22)
            gfitSim.SetTitle("fitted line")
            gfitSim.Fit("pol1")
            #gfitSim.Draw("L")

            gfitDigi = ROOT.TGraphErrors(4,x2,y2_Digi,xerr,yerrdigi)
            gfitDigi.SetName("gfitDigi")
            gfitDigi.GetXaxis().SetLimits(0.,205.)
            #gfitDigi.SetMarkerStyle(21)
            gfitDigi.SetTitle("fitted line")
            gfitDigi.Fit("pol1")
            
            
            ##################################################################
            #  Getting chi square                                            #
            ##################################################################


            #stat1 = gfitSim.TPaveStats (gfitSim.GetListOfFunctions().FindObject("stats"))
            
            fSim = gfitSim.GetFunction("pol1")
            fSim.SetLineColor(4)
            fDigi = gfitDigi.GetFunction("pol1")
            rsim = gfitSim.Fit(fSim,"S")
            rdigi= gfitDigi.Fit(fDigi,"S")
            chi2sim = rsim.Chi2()
            chi2digi = rdigi.Chi2()
            print("Chi2sim= = ",chi2sim,"\n","chi2digi = ",chi2digi)
            fSim.SetLineStyle(9)
            fSim.SetLineColor(2)

            #################################################################
            #   Plots for Digi                                              #
            #################################################################

            
            gdigi = ROOT.TGraphErrors(10,x1,y1_Digi,xerr,yerrdigi)
            gdigi.SetName("gdigi")
            gdigi.SetMarkerStyle(6)
            gdigi.SetTitle("Counted valu")
            #gdigi.Draw()
            mgdigi = ROOT.TMultiGraph()
            mgdigi.Add(gdigi)
            mgdigi.Add(gfitDigi)
            legend = ROOT.TLegend(0.1,0.7,0.48,0.9)
            legend.AddEntry("gdigi","Counted Hits ","lep")
            legend.AddEntry("f","fited  ","l")
            mgdigi.Draw("Ap")
            mgdigi.SetTitle("Global title; <PU>; number of hits")
            legend.Draw()
            ##################################################################
            #      Getting stats to print in legend                          #
            ##################################################################

            
            c1.SaveAs( 'TGraph/{0}_{1}_Digi.png'.format(rho,insn ) )
            c1.Update()
            c1.GetFrame().SetFillColor( 21 )
            c1.GetFrame().SetBorderSize( 12 )
            c1.Modified()
            c1.Update()
             

            c2 = TCanvas( 'c2', 'A Simple Graph Example', 600,400 ) 
            gsim = ROOT.TGraphErrors(10,x1,y1_Sim,xerr,yerrsim)
            gsim.SetName("gsim")
            gsim.SetMarkerStyle(6)
            gsim.SetTitle("Cunted Values")
            #gsim.Draw("P")
            mg = ROOT.TMultiGraph()

            #mgdigi.SetTitle("Global title; <PU>; number of hits")
            mg.SetTitle("{0}_{1};Pilup;nSimhits".format(rho,insn))
            mg.Add(gsim)
            mg.Add(gfitSim)
            mg.Draw("Ap")
            c2.BuildLegend()
            c2.SaveAs( 'TGraph/{0}_{1}_sim.png'.format(rho,insn ) ) 
            
            
            #c1.BuildLegend()
            #c2.SaveAs( 'TGraph/{0}_{1}_Digi.png'.format(rho,insn ) ) 
            #c2.Update()
            #c2.GetFrame().SetFillColor( 21 )
            #c2.GetFrame().SetBorderSize( 12 )
            #c2.Modified()
            #c2.Update()
            
            
            #c1.SaveAs( 'TGraph/{0}_{1}_Digi.png'.format(rho,insn ) ) 
            #c1.Update()
            #c1.GetFrame().SetFillColor( 21 )
            #c1.GetFrame().SetBorderSize( 12 )
            #c1.Modified()
            #c1.Update()
            
            #input("stop for TGraph")
            #chisquareSim,pvalueSim = stats.chisquare(ysim, predictSim_y)
            #chisquareDigi,pvalueDigi = stats.chisquare(ydigi, predictDigi_y) 
            #print("predicted y is :",predict_y)
            #if insn == nSimHits:
            
            #elif insn == 
                
            chidict["{0}_{1}_nSimHits".format(rho,insn)] = chi2sim
            chidict["{0}_{1}_nDigiHits".format(rho,insn)] = chi2digi
            
            #input("stop for predicted y")
            #plt.title("{}_".format(rho)+insn+"_nDigiHits")
            #plt.xlabel("PileUp")
            #plt.ylabel("nDigiHits")
            #plt.plot(x,[gradientDigi * i + interceptDigi for i in x],'-',c='red')
            #plt.show()
            #plt.savefig("figs/{0}_{1}_nDigiHits.png".format(rho,insn))
            #plt.close()
            
            #plt.plot(x, ysim, 'o', c ="blue")
            #plt.title("{}_".format(rho)+insn+"_nSimHits")
            #plt.xlabel("PileUp")
            #plt.ylabel("nSimHits")
            #plt.plot(x,[gradientSim * i + interceptSim for i in x],'-',c='red') 
            #plt.savefig("figs/{0}_{1}_nSimHits.png".format(rho,insn))
            #plt.close()

            #plt.plot(x, yzero, 'o', c ="blue")
            #plt.title("{}_".format(rho)+insn+"_nZero")
            #plt.xlabel("PileUp")
            #plt.ylabel("nZero")
            #plt.plot(x,predictZero_y,'-',c='red')
            #plt.savefig("figs/{0}_{1}_nZeros.png".format(rho,insn))
            #plt.close()                        
    print("len chiDict = ",len(chidict))
    v30_digi = []
    v30_sim = []
    v60_digi = []
    v60_sim = []
    v90_digi = []
    v90_sim = []
    v120_digi = []
    v120_sim = []
    rho1 = []
    rho2 =[]
    rho3 =[]
    rho4 =[]
    rho5 =[]
    rho6 =[]
    rho7 =[]
    rho8 = []
    print("chidict.key = ",chidict.keys())
    input("stop for chidict.keys")
    for key in chidict.keys():
        #print("kye = ",key.split("_",1)[1])
        #input("stop for chidict.keys")
        if key.split("_",1)[1]=="Vtsh30mV_nDigiHits":
            v30_digi.append(chidict[key])
            rho1.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh30mV_nSimHits":
            v30_sim.append(chidict[key])
            rho2.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh60mV_nSimHits":
            v60_sim.append(chidict[key])
            rho3.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh60mV_nDigiHits":
            v60_digi.append(chidict[key])
            rho4.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh90mV_nDigiHits":
            v90_digi.append(chidict[key])
            rho5.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh90mV_nSimHits":
             v90_sim.append(chidict[key])
             rho6.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh120mV_nDigiHits":
             v120_digi.append(chidict[key])
             rho7.append(key.split("_",1)[0])
        elif key.split("_",1)[1]=="Vtsh120mV_nSimHits":
            v120_sim.append(chidict[key])
            rho8.append(key.split("_",1)[0])
    print("v30_digi = ", v30_digi,"\n","rho = ",rho)
    plt.plot(rho1,v30_digi)
    plt.title("Vtsh30_nDigiHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho2,v30_sim)
    plt.title("Vtsh30_nSimHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho3,v60_sim)
    plt.title("Vtsh60_nSimHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho4,v60_digi)
    plt.title("Vtsh60_nDigiHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho5,v90_digi)
    plt.title("Vtsh90_nDigiHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho6,v90_sim)
    plt.title("Vtsh90_nSimHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho7,v120_digi)
    plt.title("Vtsh120_nDigiHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    plt.plot(rho8,v120_sim)
    plt.title("Vtsh30_nSimHits")
    plt.xlabel("Rho")
    plt.ylabel("Chi")
    plt.show()

    
    # #input("stop for len pudict:")
    # pu_len = len(opt.PU)
    # puVect=np.zeros(pu_len)
    
    # #SenDict1Keys = ['puVect','rVect', 'nZeros', 'nDigiHits', 'nDigiHitsV2', 'nSimHits', 'nUnknownsRatio', 'nOnes' , 'nUnknowns', 'nTotals']
    # AllResultsDict={}
    # AllSensors=[]
    # for sg in range( nSensorGroups ):
    #     #SensorDict = dict.fromkeys(SenDict1Keys, list())
    #     SensorDict={}
    #     nZerosList = []
    #     nZerosV0List = []
    #     nDigiHitsList = []
    #     nDigiHitsV2List = []
    #     nSimHitsList = []
    #     nUnknownsRatioList = []
    #     nOnesList = []
    #     nUnknownsList = []
    #     nTotalsList = []
    #     nTotalsMinusUnknownsList = []
    
    #     ToaRhoList = []
    #     TotRhoList = []
    #     TofRhoList = []
    #     BxTofRhoList = [] 
    #     #
    #     nTotalRhuHitsPerBxList = []
    #     nInterstedBinRhuHitsList = []
    #     nRhuZeorsList = []
    #     rhuTimingEfficiencyList = []
    #     lambdaDigiZCntRhuList = []
    #     lambdaDigiCntRhuList = []
        
    #     PeakAmplList = []
    #     RhuRhoList = []
    #     SumChargeList = []
    #     #      
    #     for pu in opt.PU:
    #         puVal=puValue(pu)
    #         puVect[opt.PU.index(pu)] = puVal


            
    #         print("pu=",pu,'\n',"puval=",puVal,'\n',"sg=",sg)
    #         print("puDict=",puDict)
    #         #input("checkpoint")





            
    #         #nZeros_data = GetData1D( puDict[pu][sg].hZeroCounting() , 1 )
    #         #nZerosList.append(nZeros_data["data"])
            
    #         nZerosV0_data = GetData1D( puDict[pu][sg].hZeroV0Counting() , 1 )
    #         nZerosV0List.append(nZerosV0_data["data"])
            
    #         nDigiHits_data = GetData1D( puDict[pu][sg].hCounting() , 1 )
    #         nDigiHitsList.append(nDigiHits_data["data"])
    
    #         nDigiHitsV2_data = GetData1D( puDict[pu][sg].hCountingV2() , 1 )
    #         nDigiHitsV2List.append(nDigiHitsV2_data["data"])
            
    #         nSimHits_data = GetData1D( puDict[pu][sg].hSimHits() , 1 )
    #         nSimHitsList.append(nSimHits_data["data"])
            
    #         nUnknownsRatio_data = GetData1D( puDict[pu][sg].hUnknownRatio() , 1 )
    #         nUnknownsRatioList.append(nUnknownsRatio_data["data"])
            
    #         nOnes_data = GetData1D( puDict[pu][sg].hOnes() , 1 )
    #         nOnesList.append(nOnes_data["data"])
            
    #         nUnknowns_data = GetData1D( puDict[pu][sg].hUnknowns() , 1 )
    #         nUnknownsList.append(nUnknowns_data["data"])
            
            
    #         nTotals_data = GetData1D( puDict[pu][sg].hNtotal() , 1 )
    #         nTotalsList.append(nTotals_data["data"])
            
    #         nTotalsMinusUnknowns_data = GetData1D( puDict[pu][sg].hNTotalsMinusUnknowns() , 1 )
    #         nTotalsMinusUnknownsList.append(nTotalsMinusUnknowns_data["data"])
            
    #         rhoVect = nTotals_data["xAxis"]
            
    #         ToaRho_data = GetData2D(puDict[pu][sg].hToaRho() , 1 , 1)
    #         #ToaRho_data.pop("xAxis")
    #         ToaRhoList.append(ToaRho_data)

    #         TotRho_data = GetData2D(puDict[pu][sg].hTotRho() , 1 , 2)
    #         #TotRho_data.pop("xAxis")
    #         TotRhoList.append(TotRho_data)

    #         TofRho_data = GetData2D(puDict[pu][sg].hTofRho() , 1 , 1)
    #         #TofRho_data.pop("xAxis")
    #         TofRhoList.append(TofRho_data)
            
    #         BxTofRho_data = GetData2D(puDict[pu][sg].hBxTofRho() , 1 , 1)
    #         #BxTofRho_data.pop("xAxis")
    #         BxTofRhoList.append(BxTofRho_data)
            
    #         ##----------
    #         tempData = GetData1D( puDict[pu][sg].hNTotalRhuHitsPerBx() , 1 )
    #         nTotalRhuHitsPerBxList.append(tempData["data"])
            
    #         tempData = GetData1D( puDict[pu][sg].hNInterstedBinRhuHits() , 1 )
    #         nInterstedBinRhuHitsList.append(tempData["data"])
            
    #         tempData = GetData1D( puDict[pu][sg].hNrhuZeors() , 1 )
    #         nRhuZeorsList.append(tempData["data"])
            
    #         tempData = GetData1D( puDict[pu][sg].hRhuTimingEfficiency() , 1 )
    #         rhuTimingEfficiencyList.append(tempData["data"])
            
    #         tempData = GetData1D( puDict[pu][sg].hLambdaDigiZCntRhu() , 1 )
    #         lambdaDigiZCntRhuList.append(tempData["data"])            

    #         tempData = GetData1D( puDict[pu][sg].hLambdaDigiCntRhu() , 1 )
    #         lambdaDigiCntRhuList.append(tempData["data"])  

            
    #         tempData = GetData2D(puDict[pu][sg].hPeakAmpl() , 1 , 1)
    #         PeakAmplList.append(tempData)
            
    #         tempData = GetData2D(puDict[pu][sg].hRhuRho() , 1 , 1)
    #         RhuRhoList.append(tempData)            
            
    #         tempData = GetData2D(puDict[pu][sg].hSumCharge() , 1 , 7)
    #         SumChargeList.append(tempData)
            
    #         ##----------
            
            
    #     SensorDict['puVect']= puVect
    #     SensorDict['rVect']= rhoVect
    #     SensorDict['nZeros']= np.array(nZerosList)
    #     SensorDict['nZerosV0']= np.array(nZerosV0List)
    #     SensorDict['nDigiHits']= np.array(nDigiHitsList)
    #     SensorDict['nDigiHitsV2']= np.array(nDigiHitsV2List)
    #     SensorDict['nSimHits']= np.array(nSimHitsList)
    #     SensorDict['nUnknownsRatio']= np.array(nUnknownsRatioList)
    #     SensorDict['nOnes']= np.array(nOnesList)
    #     SensorDict['nUnknowns']= np.array(nUnknownsList)
    #     SensorDict['nTotals']= np.array(nTotalsList)
    #     SensorDict['nTotalsMinusUnknownsList'] = np.array(nTotalsMinusUnknownsList)
        
    #     SensorDict["ToA"] = np.array(ToaRhoList)
    #     SensorDict["ToT"] = np.array(TotRhoList)
    #     SensorDict["ToF"] = np.array(TofRhoList)
    #     SensorDict["BxToF"] = np.array(BxTofRhoList)
        
    #     #
        
    #     # SensorDict["PeakAmpl"] = np.array(PeakAmplList)
    #     # SensorDict["SumSimCharge"] = np.array(SumChargeList)
    #     # SensorDict["Rhu"] = np.array(RhuRhoList)
    #     # SensorDict["TotalRhuHitsPerBx"] = np.array(nTotalRhuHitsPerBxList)
    #     # SensorDict["InterstedBinRhuHits"] = np.array(nInterstedBinRhuHitsList)
    #     # SensorDict["RhuZeors"] = np.array(nRhuZeorsList)
    #     # SensorDict["rhuTimingEff"] = np.array(rhuTimingEfficiencyList)
    #     # SensorDict["lambdaDigiZCntRhu"] = np.array(lambdaDigiZCntRhuList)
    #     # SensorDict["lambdaDigiCntRhu"] = np.array(lambdaDigiCntRhuList)
    #     #
                        
    #     AllSensors.append(SensorDict)

        
    # AllResultsDict[opt.srcType] = {"SensorGroup":AllSensors}
    # sio.savemat(destDir+"ResultsMat_{0}.mat".format(opt.srcType), AllResultsDict)
    
    
    return 0

if __name__ == "__main__":
    sys.exit( main() )
B
