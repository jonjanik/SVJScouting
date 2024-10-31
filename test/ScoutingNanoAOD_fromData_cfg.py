import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import os

# Set parameters externally 
from FWCore.ParameterSet.VarParsing import VarParsing
params = VarParsing('analysis')



params.register(
    'filterTrigger', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to ask the event to fire a trigger used in the analysis'
)

params.register(
    'filterMuons', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to ask the event to contain at least two muons'
)

params.register(
    'reducedInfo', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to store just the reduced information'
)

params.register(
    'trigProcess', 
    'HLT', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)

params.register(
    'GlobalTagData', 
    #'101X_dataRun2_HLT_v7',
    '101X_dataRun2_Prompt_v11', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)

params.register(
    'GlobalTagMC', 
    '102X_upgrade2018_realistic_v15', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)# check this


params.register(
    'fileList', 
    'none', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'input list of files'
)

params.setDefault(
    'maxEvents', 
    -1
)

params.setDefault(
    'outputFile', 
    'test.root' 
)

params.register(
  "era",
  "2018",
  VarParsing.multiplicity.singleton,VarParsing.varType.string,
  "era"
)


# Define the process
process = cms.Process("LL")

# Parse command line arguments
params.parseArguments()

# Get the era specified by user
era = params.era

# Message Logger settings
process.load("FWCore.MessageService.MessageLogger_cfi")
#if era in ["2016","2017","2018"]:
#    process.MessageLogger.destinations = ['cout', 'cerr']
#    process.MessageLogger.cerr.FwkReport.reportEvery = 1000 
#elif era in ["2022","2023","2024"]:
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.MessageLogger.cerr.FwkSummary.reportEvery = 1000
process.MessageLogger.cerr.FwkReport.reportEvery = 1000


# Set the process options -- Display summary at the end, enable unscheduled execution
process.options = cms.untracked.PSet( 
    allowUnscheduled = cms.untracked.bool(True),
    wantSummary      = cms.untracked.bool(True),
    #Rethrow = cms.untracked.vstring("ProductNotFound"), # make this exception fatal
    #Rethrow = cms.untracked.vstring()
    #FailPath = cms.untracked.vstring("ProductNotFound")
    #SkipEvent = cms.untracked.vstring('ProductNotFound')
    #TryToContinue = cms.untracked.vstring('ProductNotFound'),
)

# How many events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(params.maxEvents) )

# Input EDM files
#list = FileUtils.loadListFromFile(options.inputFiles)
#readFiles = cms.untracked.vstring(*list)

if params.fileList == "none" : readFiles = params.inputFiles
else : 
    readFiles = cms.untracked.vstring( FileUtils.loadListFromFile (os.environ['CMSSW_BASE']+'/src/PhysicsTools/ScoutingNanoAOD/test/'+params.fileList) )
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(readFiles) 
)

# Load the standard set of configuration modules
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

##--- l1 stage2 digis ---
process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )
process.load('PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff')

# Load the global tag
from Configuration.AlCa.GlobalTag import GlobalTag

global_tag_map = {
    "2018": '101X_dataRun2_Prompt_v11',
    "2022": '124X_dataRun3_Prompt_v4',
    "2023": '132X_dataRun3_Prompt_v2',
    "2024": '140X_dataRun3_Prompt_v1'
}
if era in global_tag_map:
    process.GlobalTag = GlobalTag(process.GlobalTag, global_tag_map[era], '')

# Define the services needed for the treemaker
process.TFileService = cms.Service("TFileService", 
    fileName = cms.string(params.outputFile)
)



HLTInfo = [
    "DST_DoubleMu1_noVtx_CaloScouting_v*",
    "DST_DoubleMu3_noVtx_CaloScouting_v*",
    "DST_DoubleMu3_noVtx_Mass10_PFScouting_v*",
    "DST_L1HTT_CaloScouting_PFScouting_v*",
    "DST_CaloJet40_CaloScouting_PFScouting_v*",
    "DST_HT250_CaloScouting_v*",
    "DST_HT410_PFScouting_v*",
    "DST_HT450_PFScouting_v*"]
L1Info = [
    'L1_HTT200er',
    'L1_HTT255er',
    'L1_HTT280er',
    'L1_HTT320er',
    'L1_HTT360er',
    'L1_HTT400er',
    'L1_HTT450er',
    'L1_SingleJet180',
    'L1_SingleJet200',
    'L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5',
    'L1_ETT2000']




process.mmtree = cms.EDAnalyzer('ScoutingNanoAOD_fromData' if era in ["2022","2023","2024"] else 'ScoutingNanoAOD_fromData',

    era = cms.string(params.era),
    stageL1Trigger    = cms.uint32(2),

    hltProcess=cms.string("HLT"),
    bits              = cms.InputTag("TriggerResults", "", "HLT"),
    
    triggerresults   = cms.InputTag("TriggerResults", "", params.trigProcess),
    triggerConfiguration = cms.PSet(
	    hltResults               = cms.InputTag('TriggerResults','','HLT'),
	    l1tResults               = cms.InputTag(''),
	    daqPartitions            = cms.uint32(1),
	    l1tIgnoreMaskAndPrescale = cms.bool(False),
	    throw                    = cms.bool(False)
    ),
    l1Seeds           = cms.vstring(L1Info),
    hltSeeds          = cms.vstring(HLTInfo),

    #scouting objects
    muons = cms.InputTag("hltScoutingMuonPackerNoVtx") if era in ["2022","2023","2024"]
            else cms.InputTag("hltScoutingMuonPacker"),  
    displacedVertices = cms.InputTag("hltScoutingMuonPackerNoVtx","displacedVtx") if era in ["2022","2023","2024"]
                        else cms.InputTag(""),
    electrons         = cms.InputTag("hltScoutingEgammaPacker"),
    photons           = cms.InputTag("hltScoutingEgammaPacker"),
    pfcands           = cms.InputTag("hltScoutingPFPacker"),
    pfjets            = cms.InputTag("hltScoutingPFPacker"),
    vertices          = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
    metPt             = cms.InputTag("hltScoutingPFPacker", "pfMetPt"),
    metPhi            = cms.InputTag("hltScoutingPFPacker", "pfMetPhi"),
)

process.p = cms.Path(process.mmtree)




