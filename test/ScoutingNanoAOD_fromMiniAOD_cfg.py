import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import os

# Set parameters externally 
from FWCore.ParameterSet.VarParsing import VarParsing
params = VarParsing('analysis')

params.register(
    'isMC', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether the sample is simulation or data'
)

params.register(
    'useWeights', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to use the events weights from a Monte Carlo generator'
)

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
    'xsec', 
    0.001, 
    VarParsing.multiplicity.singleton,VarParsing.varType.float,
    'Cross-section for a Monte Carlo Sample'
)#fix this

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

params.register(
    'signal', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not signal is run'
)


# Define the process
process = cms.Process("LL")

# Parse command line arguments
params.parseArguments()

# Get the era specified by user
era = params.era

# Message Logger settings
process.load("FWCore.MessageService.MessageLogger_cfi")
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
)

# How many events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(params.maxEvents) )

# Input EDM files
#list = FileUtils.loadListFromFile(options.inputFiles)
#readFiles = cms.untracked.vstring(*list)

if params.fileList == "none" : 
    readFiles = params.inputFiles
else : 
    readFiles = cms.untracked.vstring( FileUtils.loadListFromFile (os.environ['CMSSW_BASE']+'/src/PhysicsTools/ScoutingNanoAOD/test/'+params.fileList) )

process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(readFiles) 
)

# Load the standard set of configuration module
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
if params.isMC : 
    global_tag_map = {
    "2018": '106X_upgrade2018_realistic_v11_L1v1',
    "2022": '140X_mcRun3_2022_realistic_v3',
    #"2022": '124X_dataRun3_Prompt_v4',
    "2023": '130X_mcRun3_2023_realistic_v14',
    "2024": '140X_mcRun3_2024_realistic_v24'
    }
    if era in global_tag_map:
        process.GlobalTag = GlobalTag(process.GlobalTag, global_tag_map[era], '')
else :   
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

# Tree for the generator weights
process.gentree = cms.EDAnalyzer("LHEWeightsTreeMaker",
    lheInfo = cms.InputTag("externalLHEProducer"),
    genInfo = cms.InputTag("generator"),
    useLHEWeights = cms.bool(params.useWeights)
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
runSig = False
if params.signal:
  runSig = True


# Load Puppi
#
process.load('CommonTools/PileupAlgos/Puppi_cff')
# The following modification ensures that tune V15 is setup for puppi
# https://github.com/cms-sw/cmssw/blob/CMSSW_10_6_26/CommonTools/PileupAlgos/python/Puppi_cff.py#L123-L130
process.puppi.EtaMinUseDeltaZ = 2.4
process.puppi.PtMaxCharged = 20.
process.puppi.PtMaxNeutralsStartSlope = 20.
process.puppi.NumOfPUVtxsForCharged = 2
process.puppi.algos[0].etaMin = [-0.01]

process.puppi.candName = cms.InputTag('packedPFCandidates')
process.puppi.vertexName = cms.InputTag('offlineSlimmedPrimaryVertices')
process.puppi.clonePackedCands   = cms.bool(True)
process.puppi.useExistingWeights = cms.bool(False)

#define a new jet collection
from RecoJets.JetProducers.ak8PFJets_cfi import ak8PFJetsPuppi
process.ak8PFJetsPuppi  = ak8PFJetsPuppi.clone (jetPtMin = 100.)


#and add the jet collection with
from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
addJetCollection(process,labelName = 'AK8PFPUPPI', jetSource = cms.InputTag('ak8PFJetsPuppi'), algo = 'AK', rParam=0.8, genJetCollection=cms.InputTag('slimmedGenJetsAK8'),jetCorrections = ('AK8PFPuppi', ['L1FastJet', 'L2Relative', 'L3Absolute'], '\
None'),pfCandidates = cms.InputTag('packedPFCandidates'),
    pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'),
    svSource = cms.InputTag('slimmedSecondaryVertices'),
    muSource =cms.InputTag( 'slimmedMuons'),
    elSource = cms.InputTag('slimmedElectrons')
)

############################################################
#
# Setup JECs for AK8 Puppi jets
#
############################################################
# Dummy setup. L1FastJet JEC is 1 for AK8 Puppi jets
process.ak8PFPuppiL1FastjetCorrector = cms.EDProducer('L1FastjetCorrectorProducer',
    level       = cms.string('L1FastJet'),
    algorithm   = cms.string('AK8PFPuppi'),
    srcRho      = cms.InputTag('fixedGridRhoFastjetAll')
)
# MC-truth corrections  for AK8 Puppi jets
process.ak8PFPuppiL2RelativeCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2Relative'),
    algorithm = cms.string('AK8PFPuppi')
)
# Dummy setup. L2L3Residual JEC is 1 for MC
process.ak8PFPuppiL2L3ResidualCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2L3Residual'),
    algorithm = cms.string('AK8PFPuppi')
)
process.ak8PFPuppiL2L3Corrector = cms.EDProducer('ChainedJetCorrectorProducer',
    correctors = cms.VInputTag(
        'ak8PFPuppiL1FastjetCorrector',
        'ak8PFPuppiL2RelativeCorrector',
        'ak8PFPuppiL2L3ResidualCorrector',
    )
)
process.ak8PFPuppiL2L3CorrectorTask = cms.Task(
    process.ak8PFPuppiL1FastjetCorrector,
    process.ak8PFPuppiL2RelativeCorrector,
    process.ak8PFPuppiL2L3ResidualCorrector,
    process.ak8PFPuppiL2L3Corrector,
)
process.ak8PFPuppiL2L3CorrectorSeq = cms.Sequence(process.ak8PFPuppiL2L3CorrectorTask)

############################################################
#
# Setup JECs for HLT AK4 PF jets
#
############################################################
# Dummy setup. L1FastJet JEC is 1 for HLT AK4 PF jets
process.ak4PFHLTL1FastjetCorrector = cms.EDProducer('L1FastjetCorrectorProducer',
    level       = cms.string('L1FastJet'),
    algorithm   = cms.string('AK4PFHLT'),
    srcRho      = cms.InputTag('fixedGridRhoFastjetAll')
)
# MC-truth corrections  for HLT AK8 PF jets
process.ak4PFHLTL2RelativeCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2Relative'),
    algorithm = cms.string('AK4PFHLT')
)
# Dummy setup. L2L3Residual JEC is 1 for MC
process.ak4PFHLTL2L3ResidualCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2L3Residual'),
    algorithm = cms.string('AK4PFHLT')
)
process.ak4PFHLTL2L3Corrector = cms.EDProducer('ChainedJetCorrectorProducer',
    correctors = cms.VInputTag(
        'ak4PFHLTL1FastjetCorrector',
        'ak4PFHLTL2RelativeCorrector',
        'ak4PFHLTL2L3ResidualCorrector',
    )
)
process.ak4PFHLTL2L3CorrectorTask = cms.Task(
    process.ak4PFHLTL1FastjetCorrector,
    process.ak4PFHLTL2RelativeCorrector,
    process.ak4PFHLTL2L3ResidualCorrector,
    process.ak4PFHLTL2L3Corrector,
)
process.ak4PFHLTL2L3CorrectorSeq = cms.Sequence(process.ak4PFHLTL2L3CorrectorTask)


############################################################
#
# Setup JECs for HLT AK8 PF jets
#
############################################################
# Dummy setup. L1FastJet JEC is 1 for HLT AK8 PF jets
process.ak8PFHLTL1FastjetCorrector = cms.EDProducer('L1FastjetCorrectorProducer',
    level       = cms.string('L1FastJet'),
    algorithm   = cms.string('AK8PFHLT'),
    srcRho      = cms.InputTag('fixedGridRhoFastjetAll')
)
# MC-truth corrections  for HLT AK8 PF jets
process.ak8PFHLTL2RelativeCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2Relative'),
    algorithm = cms.string('AK8PFHLT')
)
# Dummy setup. L2L3Residual JEC is 1 for MC
process.ak8PFHLTL2L3ResidualCorrector = cms.EDProducer('LXXXCorrectorProducer',
    level     = cms.string('L2L3Residual'),
    algorithm = cms.string('AK8PFHLT')
)
process.ak8PFHLTL2L3Corrector = cms.EDProducer('ChainedJetCorrectorProducer',
    correctors = cms.VInputTag(
        'ak8PFHLTL1FastjetCorrector',
        'ak8PFHLTL2RelativeCorrector',
        'ak8PFHLTL2L3ResidualCorrector',
    )
)
process.ak8PFHLTL2L3CorrectorTask = cms.Task(
    process.ak8PFHLTL1FastjetCorrector,
    process.ak8PFHLTL2RelativeCorrector,
    process.ak8PFHLTL2L3ResidualCorrector,
    process.ak8PFHLTL2L3Corrector,
)
process.ak8PFHLTL2L3CorrectorSeq = cms.Sequence(process.ak8PFHLTL2L3CorrectorTask)


process.mmtree = cms.EDAnalyzer('ScoutingNanoAOD_fromMiniAOD',
    doL1              = cms.bool(False),
    doData            = cms.bool(not params.isMC and not params.signal),
    doSignal          = cms.bool(runSig), 
    isMC              = cms.bool(params.isMC),
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
    ReadPrescalesFromFile = cms.bool( False ),
    AlgInputTag = cms.InputTag("gtStage2Digis"),
    l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
    l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
    l1Seeds           = cms.vstring(L1Info),
    hltSeeds          = cms.vstring(HLTInfo),
    GetLumiInfoHeader=cms.InputTag("generator"),

    #scouting objects
    muons             = cms.InputTag("hltScoutingMuonPackerCalo"),
    electrons         = cms.InputTag("hltScoutingEgammaPacker"),
    photons           = cms.InputTag("hltScoutingEgammaPacker"),
    pfcands           = cms.InputTag("hltScoutingPFPacker"),
    pfjets            = cms.InputTag("hltScoutingPFPacker"),
    vertices          = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
    metPt             = cms.InputTag("hltScoutingPFPacker", "pfMetPt"),
    metPhi            = cms.InputTag("hltScoutingPFPacker", "pfMetPhi"),

    #HLT AK4 PF jets
    applyJECForAK4Scout=cms.bool(True),
    jetCorrectorHLTAK4=cms.InputTag("ak4PFHLTL2L3Corrector"),
    jetAK4ScoutPtMin=cms.double(20),
    
    #HLT AK8 PF jets
    applyJECForAK8Scout=cms.bool(True),
    jetCorrectorHLTAK8=cms.InputTag("ak8PFHLTL2L3Corrector"),
    jetAK8ScoutPtMin=cms.double(100),

    #offline objects
    pfcandsReco=cms.InputTag("packedPFCandidates"),
    ak4pfjetsReco=cms.InputTag("slimmedJetsPuppi"),

    verticesReco=cms.InputTag('offlineSlimmedPrimaryVertices'),
    electronsReco=cms.InputTag("slimmedElectrons"),
    muonsReco=cms.InputTag("slimmedMuons"),
    metReco=cms.InputTag("slimmedMETs"),
    PuppimetReco=cms.InputTag("slimmedMETsPuppi"),

    #Puppi AK8 PF
    ak8pfjetsReco=cms.InputTag("ak8PFJetsPuppi"),
    applyJECForAK8=cms.bool(True),
    jetCorrectorAK8=cms.InputTag("ak8PFPuppiL2L3Corrector"),
    jetAK8PtMin=cms.double(100),

    #gen info and pileup
    genak4jets        = cms.InputTag("slimmedGenJets"),
    genak8jets        = cms.InputTag("slimmedGenJetsAK8"),
    pileupinfo        = cms.InputTag("addPileupInfo"),
    pileupinfo_sig    = cms.InputTag("slimmedAddPileupInfo"),
    geneventinfo     = cms.InputTag("generator"),
    gens             = cms.InputTag("prunedGenParticles"),
    rho               = cms.InputTag("fixedGridRhoFastjetAllScouting"),
    rho2              = cms.InputTag("hltScoutingPFPacker","rho"),

)


#if(params.isMC):
#if(runSig or (params.isMC and not params.era=="2016")):
#if(runSig):
#if(params.signal):
  #print("test1",runSig,params.isMC,params.era,(params.isMC and not params.era=="2016"))
# from PhysicsTools.PatUtils.l1PrefiringWeightProducer_cfi import l1PrefiringWeightProducer
# process.prefiringweight = l1PrefiringWeightProducer.clone(
# ThePhotons           = cms.InputTag("hltScoutingEgammaPacker"),
# TheMuons             = cms.InputTag("hltScoutingMuonPacker"),
# TheJets            = cms.InputTag("hltScoutingPFPacker"),
# #TheJets = cms.InputTag("slimmedJets"), #this should be the slimmedJets collection with up to date JECs 
# #TheJets = cms.InputTag("updatedPatJetsUpdatedJEC"), #this should be the slimmedJets collection with up to date JECs 
# DataEraECAL = cms.string("2017BtoF"), #Use 2016BtoH for 2016
# DataEraMuon = cms.string("20172018"), #Use 2016 for 2016
# UseJetEMPt = cms.bool(False),
# PrefiringRateSystematicUnctyECAL = cms.double(0.2),
# PrefiringRateSystematicUnctyMuon = cms.double(0.2)
# )
#process.p = cms.Path(process.puppi * process.ak8PFJetsPuppi * process.ak8PFPuppiL2L3CorrectorSeq * process.ak8PFHLTL2L3CorrectorSeq * process.ak4PFHLTL2L3CorrectorSeq * process.prefiringweight* process.mmtree)
# process.p = cms.Path(process.puppi * process.ak8PFPuppiL2L3CorrectorSeq * process.ak8PFHLTL2L3CorrectorSeq * process.ak4PFHLTL2L3CorrectorSeq * process.prefiringweight* process.mmtree)

#else:
process.p = cms.Path(process.puppi * process.ak8PFPuppiL2L3CorrectorSeq * process.ak8PFHLTL2L3CorrectorSeq * process.ak4PFHLTL2L3CorrectorSeq * process.mmtree)



