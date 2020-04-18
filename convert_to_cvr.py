from castvoterecords import Code, Candidate, Party, IdentifierType, CandidateContest, VoteVariation, CandidateSelection, ContestSelection, CVRContestSelection, CVRContest, CVRSnapshot, CVR, Election, GpUnit, ReportingUnitType, CastVoteRecordReport, ReportingDevice, BallotMeasureContest, BallotMeasureSelection

import csv
from itertools import islice
import argparse


parser = argparse.ArgumentParser(description='Convert an ESS Report into a NIS CVR XML')
parser.add_argument("--file", help="CSV input file to process. Default is ward9_fall18.csv", default="ward9_fall18.csv")
parser.add_argument("--all", help= "Process entire file instead of only 10 rows", action="store_true")
args = parser.parse_args()

#
# We'll build the CVR up from the bottom. First, we'll create the political parties that appear in this CVR
#
dem = Party(abbreviation='DEM', name='Democratic', id = "_Dem")
gop = Party(abbreviation='GOP', name='Republican', id = "_GOP")
lib = Party(abbreviation='LIB', name='Libertarian', id = "_Lib")
wgr = Party(abbreviation='WGR', name='Wisconsin Green', id = "_Grn")
wip = Party(abbreviation='WIP', name='The Wisconsin Party', id = "_Wip")
con = Party(abbreviation='CON', name='Constitution', id = "_Con")

parties = [dem, gop, lib, wgr, wip, con]

#
# Codes are used to figure out some types when parsing the report. 
# I don't know what 'value' is supposed to be
#
wisc_statewide_code = Code(code_type = IdentifierType.STATE_LEVEL, value='Wisconsin')
federal_code = Code(code_type = IdentifierType.NATIONAL_LEVEL, value='United States')
dane_code = Code(code_type = IdentifierType.LOCAL_LEVEL, value='County of Dane')

# Now we'll make some candidates, and allow for them to be used as "selections" on ballots
# We'll start with Governor candidates
evers = Candidate(party=dem, code=wisc_statewide_code, name=u"DEM Tony Evers /Mandela Barnes", id="_GOV_Evers")
evers_selection = CandidateSelection(candidate=evers, id="_sel_GOV_Evers")

walker = Candidate(party=gop, code=wisc_statewide_code, name=u"REP Scott Walker /Rebecca Kleefisch", id="_GOV_Walker")
walker_selection = CandidateSelection(candidate=walker, id="_sel_GOV_Walker")

anderson = Candidate(party=lib, code=wisc_statewide_code, name=u"LIB Phillip Anderson /Patrick Baird", id="_GOV_Anderson")
anderson_selection = CandidateSelection(candidate=anderson, id="_sel_GOV_Anderson")

white = Candidate(party=wgr, code=wisc_statewide_code, name=u"WGR Michael J. White /Tiffany Anderson", id="_GOV_White")
white_selection = CandidateSelection(candidate=white, id="_sel_GOV_White")

enz = Candidate(party=wip, code=wisc_statewide_code, name=u"WIP Arnie Enz /No Candidate", id="_GOV_Enz")
enz_selection = CandidateSelection(candidate=enz, id="_sel_GOV_Enz")

# note: no party for Maggie Turnbull
turnbull = Candidate(code=wisc_statewide_code, name=u"IND Maggie Turnbull /Wil Losch", id="_GOV_Turnbull")
turnbull_selection = CandidateSelection(candidate=turnbull, id="_sel_GOV_Turnbull")

gov_writein = Candidate(code=wisc_statewide_code, name="write-in:", id="_GOV_write-in")
gov_writein_selection = CandidateSelection(candidate=gov_writein, is_write_in=True, id="_sel_GOV_write-in")

# Having a list of candidates is handy for later. Also, we'll want a map of candidate names
# back to the selection, so we can look those up later
gov_candidates = [walker, evers, anderson, white, turnbull, enz, gov_writein]
gov_sels = {}
for c in [walker_selection, evers_selection, anderson_selection, white_selection, enz_selection, turnbull_selection, gov_writein_selection]:
	gov_sels[c.candidate.name] = c

#
# Once we've got all the candidates created, we'll create a contest to put them all in
# TODO: add a helper in the CandidateContest object to look up a contest selection given a name
#
gov_contest = CandidateContest(name='Governor / Lieutenant Governor', vote_variation=VoteVariation.N_OF_M, contest_selections=[walker_selection, evers_selection, anderson_selection, white_selection, turnbull_selection, enz_selection, gov_writein_selection], id="_Contest_GOV")

# Repeat for Attorneys General
schimel = Candidate(party=gop, code=wisc_statewide_code, name="REP Brad Schimel", id="_ag_schmiel")
schimel_selection = CandidateSelection(candidate=schimel, id="_sel_ag_schmiel")

kaul = Candidate(party=dem, code=wisc_statewide_code, name="DEM Josh Kaul", id="_ag_kaul")
kaul_selection = CandidateSelection(candidate=kaul, id="_sel_ag_kaul")

larson = Candidate(party=con, code=wisc_statewide_code, name="CON Terry Larson", id="_ag_larson")
larson_selection = CandidateSelection(candidate=larson, id="_sel_ag_larson")

ag_writein = Candidate(code=wisc_statewide_code, name="write-in:", id="_AG_write-in")
ag_writein_selection = CandidateSelection(candidate=ag_writein, is_write_in=True, id="_sel_AG_write-in")

ag_candidates = [schimel, kaul, larson, ag_writein]
ag_sels = {}
for c in [schimel_selection, kaul_selection, larson_selection, ag_writein_selection]:
	ag_sels[c.candidate.name] = c

ag_contest = CandidateContest(name='Attorney General', vote_variation=VoteVariation.N_OF_M, contest_selections=[schimel_selection, kaul_selection, larson_selection, ag_writein_selection], id="_Contest_AG")

# sec state
lafollette = Candidate(party=dem, code=wisc_statewide_code, name="DEM Doug La Follette", id="_sos_lafollette")
lafollette_selection = CandidateSelection(candidate=lafollette, id="_sel_sos_lafollette")

schroeder = Candidate(party=gop, code=wisc_statewide_code, name="REP Jay Schroeder", id="_sos_schroeder")
schroeder_selection = CandidateSelection(candidate=schroeder, id="_sel_sos_schroeder")

sos_writein = Candidate(code=wisc_statewide_code, name="write-in:", id="_SOS_write-in")
sos_writein_selection = CandidateSelection(candidate=sos_writein, is_write_in=True, id="_sel_SOS_write-in")

sos_candidates = [schroeder, lafollette, sos_writein]
sos_sels = {}
for c in [schroeder_selection, lafollette_selection, sos_writein_selection]:
	sos_sels[c.candidate.name] = c

sos_contest = CandidateContest(name='Secretary of State', vote_variation=VoteVariation.N_OF_M, contest_selections=[schroeder_selection, lafollette_selection, sos_writein_selection], id="_Contest_SOS")

# Treasurer
hartwig = Candidate(party=gop, code=wisc_statewide_code, name="REP Travis Hartwig", id="_tres_hartwig")
hartwig_selection = CandidateSelection(candidate=hartwig, id="_sel_tres_hartwig")

godlewski = Candidate(party=dem, code=wisc_statewide_code, name="DEM Sarah Godlewski", id="_tres_godlewski")
godlewski_selection = CandidateSelection(candidate=godlewski, id="_sel_tres_godlewski")

zuelke = Candidate(party=con, code=wisc_statewide_code, name="CON Andrew Zuelke", id="_ag_zuelke")
zuelke_selection = CandidateSelection(candidate=zuelke, id="_sel_ag_zuelke")

tres_writein = Candidate(code=wisc_statewide_code, name="write-in:", id="_TRES_write-in")
tres_writein_selection = CandidateSelection(candidate=tres_writein, is_write_in=True, id="_sel_TRES_write-in")

tres_candidates = [hartwig, godlewski, zuelke, tres_writein]
tres_sels = {}
for c in [hartwig_selection, godlewski_selection, zuelke_selection, tres_writein_selection]:
	tres_sels[c.candidate.name] = c

tres_contest = CandidateContest(name='State Treasurer', vote_variation=VoteVariation.N_OF_M, contest_selections=[hartwig_selection, godlewski_selection, zuelke_selection, tres_writein_selection], id="_Contest_TRES")

# senate 
baldwin = Candidate(party=dem, code=federal_code, name="DEM Tammy Baldwin", id="_ussen_baldwin")
baldwin_selection = CandidateSelection(candidate=baldwin, id="_sel_ussen_baldwin")

vukmir = Candidate(party=gop, code=federal_code, name="REP Leah Vukmir", id="_ussen_vukmir")
vukmir_selection = CandidateSelection(candidate=vukmir, id="_sel_ussen_vukmir")

ussen_writein = Candidate(code=federal_code, name="write-in:", id="_ussen_write-in")
ussen_writein_selection = CandidateSelection(candidate=ussen_writein, is_write_in=True, id="_sel_ussen_write-in")

ussen_candidates = [vukmir, baldwin, ussen_writein]
ussen_sels = {}
for c in [vukmir_selection, baldwin_selection, ussen_writein_selection]:
	ussen_sels[c.candidate.name] = c

ussen_contest = CandidateContest(name='United States Senator', vote_variation=VoteVariation.N_OF_M, contest_selections=[vukmir_selection, baldwin_selection, ussen_writein_selection], id="_Contest_USSEN")

# house 
pocan = Candidate(party=dem, code=federal_code, name="DEM Mark Pocan", id="_ushouse_pocan")
pocan_selection = CandidateSelection(candidate=pocan, id="_sel_ushouse_pocan")

house_writein = Candidate(code=federal_code, name="write-in:", id="_ushouse_write-in")
house_writein_selection = CandidateSelection(candidate=house_writein, is_write_in=True, id="_sel_ushouse_write-in")

house_candidates = [pocan, house_writein]
house_sels = {}
for c in [pocan_selection, house_writein_selection]:
	house_sels[c.candidate.name] = c

house_contest = CandidateContest(name='Representative in Congress District 2', vote_variation=VoteVariation.N_OF_M, contest_selections=[pocan_selection, house_writein_selection], id="_Contest_USHOUSE")

# assembly 
sargent = Candidate(party=dem, code=wisc_statewide_code, name="DEM Melissa Agard Sargent", id="_wiassembly_sargent")
sargent_selection = CandidateSelection(candidate=sargent, id="_sel_wiassembly_sargent")

assembly_writein = Candidate(code=wisc_statewide_code, name="write-in:", id="_wiassembly_write-in")
assembly_writein_selection = CandidateSelection(candidate=assembly_writein, is_write_in=True, id="_sel_wiassembly_write-in")

assembly_candidates = [sargent, assembly_writein]
assembly_sels = {}
for c in [sargent_selection, assembly_writein_selection]:
	assembly_sels[c.candidate.name] = c

assembly_contest = CandidateContest(name='Representative to the Assembly District 48', vote_variation=VoteVariation.N_OF_M, contest_selections=[sargent_selection, assembly_writein_selection], id="_Contest_WIAssembly48")

# sheriff 
mahoney = Candidate(party=dem, code=dane_code, name="DEM David J. Mahoney", id="_danesheriff_mahoney")
mahoney_selection = CandidateSelection(candidate=mahoney, id="_sel_danesheriff_mahoney")

sheriff_writein = Candidate(code=dane_code, name="write-in:", id="_danesheriff_write-in")
sheriff_writein_selection = CandidateSelection(candidate=sheriff_writein, is_write_in=True, id="_sel_danesheriff_write-in")

sheriff_candidates = [mahoney, sheriff_writein]
sheriff_sels = {}
for c in [mahoney_selection, sheriff_writein_selection]:
	sheriff_sels[c.candidate.name] = c

sheriff_contest = CandidateContest(name='Sheriff Dane County', vote_variation=VoteVariation.N_OF_M, contest_selections=[mahoney_selection, sheriff_writein_selection], id="_Contest_DaneSheriff")

# clerk of courts 
esqueda = Candidate(party=dem, code=dane_code, name="DEM Carlo Esqueda", id="_danecoc_esqueda")
esqueda_selection = CandidateSelection(candidate=esqueda, id="_sel_danecoc_esqueda")

danecoc_writein = Candidate(code=dane_code, name="write-in:", id="_danecoc_write-in")
danecoc_writein_selection = CandidateSelection(candidate=danecoc_writein, is_write_in=True, id="_sel_danecoc_write-in")

danecoc_candidates = [esqueda, danecoc_writein]
danecoc_sels = {}
for c in [esqueda_selection, danecoc_writein_selection]:
	danecoc_sels[c.candidate.name] = c

danecoc_contest = CandidateContest(name='Clerk of Circuit Court Dane County', vote_variation=VoteVariation.N_OF_M, contest_selections=[esqueda_selection, danecoc_writein_selection], id="_Contest_DaenCOC")

weed_yes_selection = BallotMeasureSelection(selection='Yes', id="_sel_weed_yes")
weed_no_selection = BallotMeasureSelection(selection='No', id="_sel_weed_no")
weed_sels = {}
weed_sels['Yes'] = weed_yes_selection
weed_sels['No'] = weed_no_selection

weed_referenda = BallotMeasureContest(name="County Referendum re: legalize marijuana", vote_variation=VoteVariation.N_OF_M, contest_selections=[weed_yes_selection, weed_no_selection], id="_Contest_Weed")

tax_yes_selection = BallotMeasureSelection(selection='Yes', id="_sel_tax_yes")
tax_no_selection = BallotMeasureSelection(selection='No', id="_sel_tax_no")
tax_sels = {}
tax_sels['Yes'] = tax_yes_selection
tax_sels['No'] = tax_no_selection

tax_referenda = BallotMeasureContest(name="County Referendum re: tax loopholes", vote_variation=VoteVariation.N_OF_M, contest_selections=[tax_yes_selection, tax_no_selection], id="_Contest_Tax")

#
# Now we need to set up some bookkeeping to do fill out about what the specifics of the election
#
# First up is details about where we the election happened and what equipment was used
local_precinct_code = Code(code_type = IdentifierType.LOCAL_LEVEL, value = "City of Madison Ward 9")
ward9 = GpUnit(name='Ward 9', gp_type = ReportingUnitType.PRECINCT, id = '_cvr_gp', code=local_precinct_code)
ward9_tabulator = ReportingDevice(id='_rpdev_ward9', model='ESS DS200', notes='Reporting Device used for Madison Ward 9')

# 
# Now we write down where all the details about what contests and candidates were on the ballot. 
# This is separate from the 'CVR' data so it's not repeated in every record
# Note: I think I have the election ID, name, and scope wrong - it's probably supposed to be 'Statewide'
#
fall18_wd9 = Election(id = '_fall_2018_madison_ward_9', name='Fall 2018 Ward 9', election_scope = ward9, contests = [gov_contest, ag_contest, sos_contest, tres_contest, ussen_contest, house_contest, assembly_contest, sheriff_contest, danecoc_contest, weed_referenda, tax_referenda], candidates = gov_candidates + ag_candidates + sos_candidates + tres_candidates + ussen_candidates + house_candidates + assembly_candidates + sheriff_candidates + danecoc_candidates)

# 
# The CSV included is ~2300 ballots with a whole slug of different offices to be elected.
#

ward9_file = open(args.file)
ward9_data = csv.DictReader(ward9_file)

cvrs = []

limit = 10
if args.all:
	limit = None
for row in islice(ward9_data, limit):
	cvr_id = row['Cast Vote Record']

	cvr_contests = []

# A CVRContest is an actual vote record for a specific office- it refers to the objects we created earlier to get the common data
# So this first object is saying 'This is a vote in the gov contest and it's a vote for Tony Evers'
# Then the second object is saying 'This is a vote in the ag contest and it's a vote for Josh Kaul' 
# Note that they're specific to individual voters - the CVRContest for Gov object (and CVRContesttSelection object) from ballot 239377 is a different 
# object from the CVRContest 
# for Gov for 269378, even though they're both for Evers - they could be marked differently or whatever, so the NIST CVR Standard treats them as different objects

	# I am probably going to hell for this
	contests = [
			('Governor / Lieutenant Governor', gov_sels, gov_contest, 'gov'),
			('Attorney General', ag_sels, ag_contest, 'ag'),
			('Secretary of State', sos_sels, sos_contest, 'sos'),
			('State Treasurer', tres_sels, tres_contest, 'tres'),
			('United States Senator', ussen_sels, ussen_contest, 'ussen'),
			('Representative in Congress District 2', house_sels, house_contest, 'ushouse'),
			('Representative to the Assembly District 48', assembly_sels, assembly_contest, 'wiassem48'),
			('Sheriff Dane County', sheriff_sels, sheriff_contest, 'danesheriff'),
			('Clerk of Circuit Court Dane County', danecoc_sels, danecoc_contest, 'danecoc'),
			('County Referendum re: tax loopholes', tax_sels, tax_referenda, 'tax'),
			('County Referendum re: legalize marijuana', weed_sels, weed_referenda, 'weed')	
			]
	for c in contests: 
		selection = row[c[0]]
		choices = c[1]
		contest = c[2]
		suffix = c[3]


		if selection == 'overvote':
			cvr_contest = CVRContest(contest=contest, 
						id='_cvr_contest_{}_{}'.format(cvr_id, suffix), 
						overvotes = 1)
		elif selection == 'undervote':
			cvr_contest = CVRContest(contest=contest, 
						id='_cvr_contest_{}_{}'.format(cvr_id, suffix), 
						undervotes = 1)
		else:
			cvr_contest_selection = CVRContestSelection(contest_selection = choices[selection], id= '_cvr{}_cs_{}'.format(cvr_id, suffix))
			cvr_contest = CVRContest(contest=contest, 
						id='_cvr_contest_{}_{}'.format(cvr_id, suffix), 
						cvr_contest_selection=[cvr_contest_selection]
						)
		cvr_contests.append(cvr_contest)
		# end of processing a single contest for loop
	# end of loop over all contests on a single ballot

#
# Now we put actual ballot together - we take the choices from ballot and bundle them together as a 'Snapshot', and wrap them in a 'CVR'
# We also need to say what election this is for, which is why we had to create that object before setting up the specific CVR records
#
	cvr = CVR(id="_cvr_{}".format(cvr_id), 
			election=fall18_wd9, 
			cvr_snapshot=[CVRSnapshot(id='_cvr_snapshot_{}_001'.format(cvr_id), cvr_contests=cvr_contests)]
			)

	cvrs.append(cvr)
#end of processing all ballots

#
# Finally, put the election metadata together with the ballot-level results and call it a report.
#
fall18_wd9_cvr_report = CastVoteRecordReport(election=fall18_wd9, cvrs = cvrs, gp_unit = ward9, reporting_device = ward9_tabulator, parties = parties)
fall18_wd9_cvr_report.to_xml()


