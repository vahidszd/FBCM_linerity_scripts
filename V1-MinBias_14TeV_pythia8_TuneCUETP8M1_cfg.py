# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: --evt_type MinBias_14TeV_pythia8_TuneCUETP8M1_cfi -s GEN,SIM --mc --fileout file:V1_MinBias_14TeV_pythia8_TuneCUETP8M1_GEN_SIM.root --conditions auto:phase2_realistic --era Phase2 --datatier GEN-SIM --geometry Extended2026D81 --eventcontent FEVTDEBUG --pileup AVE_200_BX_25ns,{'B':(-3,3),'N':1.5} --python_filename V1-MinBias_14TeV_pythia8_TuneCUETP8M1_cfg.py --customise Configuration/DataProcessing/Utils.addMonitoring --nThreads 8 -n 40 --no_exe
import FWCore.ParameterSet.Config as cms

import os
def getInputFileList(baseDirectory, beginsWithTheseChars ): # without "/" at the end
    # baseDirectory ='/eos/cms/store/group/dpg_bril/comm_bril/phase2-sim/FBCM/Aug2022Workshop/MinBias/FBCMV2MinBias/220820_202455'
    # baseDir = "/".join(baseDirectory.split('/')[:-1]) + "/"
    baseDir = baseDirectory + "/"
    storeDir = "/" + "/".join(baseDir.split('/')[3:])
    subDirs = os.listdir(baseDir)
    minBiasFiles = []
    for folder in subDirs:
        minBiasDirectory = baseDir + folder
        filesinDirectory = [storeDir + folder + "/" + f for f in os.listdir(minBiasDirectory) if f[:len(beginsWithTheseChars)] == beginsWithTheseChars]
        minBiasFiles = minBiasFiles + filesinDirectory
    return minBiasFiles


baseDirectory ='/eos/cms/store/group/dpg_bril/comm_bril/phase2-sim/FBCM/Aug2022Workshop/MinBias/FBCMV2MinBias/220820_202455'
minBiasFiles = getInputFileList(baseDirectory, "MinBias" )

import FWCore.ParameterSet.VarParsing as VarParsing

options = VarParsing.VarParsing ('analysis')
options.register ('pu',
                  1.5, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.string,          # string, int, or float
                  "number of pile up events")
options.register ('aging',
                  0, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.float,          # string, int, or float
                  "number of pile up events")
options.parseArguments()

from Configuration.Eras.Era_Phase2_cff import Phase2
#from SimGeneral.MixingModule.mix_2018_25ns_UltraLegacy_PoissonOOTPU_cfi import *#for pileUp test
process = cms.Process('SIM',Phase2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mix_POISSON_average_cfi')
#process.load("SimGeneral.MixingModule.mix_2018_25ns_ProjectedPileup_PoissonOOTPU_cfi")#added by me to check pileup config

process.load('Configuration.Geometry.GeometryExtended2026D81Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D81_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic50ns13TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(400),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("EmptySource")
#process.source = cms.Source("PoolSource",
#fileName =cms.PSet(files =  cms.untracked.vstring(minBiasFiles))
#)#changed by me to add pileup

process.options = cms.untracked.PSet(
    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    SkipEvent = cms.untracked.vstring(),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(1)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    makeTriggerResults = cms.obsolete.untracked.bool,
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(1),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('MinBias_14TeV_pythia8_TuneCUETP8M1_cfi nevts:400'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
if options.pu == '0.5':
    outFName = 'histo_pu0p5.root' 
elif options.pu == '1.5':
    print("hi")
    outFName = 'histo_pu1p5.root'
else:     
    outFName = 'histo_pu{0}.root'.format( options.pu )

process.FEVTDEBUGoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM'),
        filterName = cms.untracked.string('')
    ),
                                           fileName = cms.untracked.string(outFName),
    outputCommands = process.FEVTDEBUGEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
# process.mix = cms.EDProducer("MixingModule",
#     bunchspace = cms.int32(25),
#     minBunch = cms.int32(-3),
#     maxBunch = cms.int32(3),
#     maxNbPileupEvents = cms.int32(20),
#     input = cms.InputTag("digi2raw"),
#     signal = cms.InputTag("simG4FullSimHits"),
#     label = cms.string("mix")
# )
#process.mix.input.nbPileupEvents = cms.PSet(averageNumber = cms.double(float(options.pu)))
process.mix.input.nbPileupEvents.averageNumber = cms.double(float(options.pu))
process.mix.bunchspace = cms.int32(25)
process.mix.minBunch = cms.int32(-3)
process.mix.maxBunch = cms.int32(3)
#process.mix.input.fileNames = cms.untracked.vstring(minBiasFiles)
process.mix.input.fileNames = cms.untracked.vstring(['file:/eos/cms/store/group/dpg_bril/comm_bril/phase2-sim/FBCM/Aug2022Workshop/MinBias/FBCMV2MinBias/220820_202455/0000/MinBias_14TeV_pythia8_TuneCUETP8M1_GEN_SIM_999.root'])
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')

process.generator = cms.EDFilter("Pythia8GeneratorFilter",
    PythiaParameters = cms.PSet(
        parameterSets = cms.vstring(
            'pythia8CommonSettings', 
            'pythia8CUEP8M1Settings', 
            'processParameters'
        ),
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on', 
            'SoftQCD:singleDiffractive = on', 
            'SoftQCD:doubleDiffractive = on'
        ),
        pythia8CUEP8M1Settings = cms.vstring(
            'Tune:pp 14', 
            'Tune:ee 7', 
            'MultipartonInteractions:pT0Ref=2.4024', 
            'MultipartonInteractions:ecmPow=0.25208', 
            'MultipartonInteractions:expPow=1.6'
        ),
        pythia8CommonSettings = cms.vstring(
            'Tune:preferLHAPDF = 2', 
            'Main:timesAllowErrors = 10000', 
            'Check:epTolErr = 0.01', 
            'Beams:setProductionScalesFromLHEF = off', 
            'SLHA:minMassSM = 1000.', 
            'ParticleDecays:limitTau0 = on', 
            'ParticleDecays:tau0Max = 10', 
            'ParticleDecays:allowPhotonRadiation = on'
        )
    ),
    comEnergy = cms.double(14000.0),
    crossSection = cms.untracked.double(71390000000.0),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(1)
)


process.demo = cms.EDAnalyzer('SimHitAnalyzer',
 InstanceNameTags = cms.vstring(
'Vtsh30mV', 
'Vtsh60mV',
'Vtsh90mV',
'Vtsh120mV'), # provide a list of valid instanse 
TreeName = cms.vstring( 'PU{0}'.format(options.pu)),
hitsProducer = cms.string('g4SimHits'),
SubdetName = cms.string('FBCMHits'),
simHits = cms.InputTag("g4SimHits", "FBCMHits")
)

process.TFileService = cms.Service("TFileService",
                                       fileName = cms.string(outFName)
                                   )

process.ProductionFilterSequence = cms.Sequence(process.generator)

# Path and EndPath definitions
process.analyze_step = cms.Path(process.demo)
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Sequence(process.psim)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGoutput_step = cms.EndPath(process.FEVTDEBUGoutput)

# Schedule definition
#process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.simulation_step,process.endjob_step,process.analyze_step)

process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.simulation_step,process.endjob_step,process.FEVTDEBUGoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads=cms.untracked.uint32(2)
process.options.numberOfStreams=cms.untracked.uint32(0)
process.options.numberOfConcurrentLuminosityBlocks=cms.untracked.uint32(1)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path).insert(0, process.ProductionFilterSequence)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
