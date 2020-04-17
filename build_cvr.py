from castvoterecords import Code, Candidate, Party, IdentifierType, CandidateContest, VoteVariation, CandidateSelection, ContestSelection, CVRContestSelection, CVRContest, CVRSnapshot, CVR, Election, GpUnit, ReportingUnitType, CastVoteRecordReport, ReportingDevice, BallotMeasureContest, BallotMeasureSelection

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

gov_candidates = [walker, evers, anderson, white, turnbull, enz, gov_writein]

# Once we've got all the candidates created, we'll create a contest to put them all in
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

ag_contest = CandidateContest(name='Attorney General', vote_variation=VoteVariation.N_OF_M, contest_selections=[schimel_selection, kaul_selection, larson_selection, ag_writein_selection], id="_Contest_AG")

weed_yes_selection = BallotMeasureSelection(selection='Yes', id="_sel_weed_yes")
weed_no_selection = BallotMeasureSelection(selection='No', id="_sel_weed_no")

weed_referenda = BallotMeasureContest(name="County Referendum re: legalize marijuana", vote_variation=VoteVariation.N_OF_M, contest_selections=[weed_yes_selection, weed_no_selection], id="_Contest_Weed")

tax_yes_selection = BallotMeasureSelection(selection='Yes', id="_sel_tax_yes")
tax_no_selection = BallotMeasureSelection(selection='No', id="_sel_tax_no")

tax_referenda = BallotMeasureContest(name="County Referendum re: tax loopholes", vote_variation=VoteVariation.N_OF_M, contest_selections=[tax_yes_selection, tax_no_selection], id="_Contest_Tax")

#
# Now we need to set up some bookkeeping to do fill out about what the specifics of the election
#
# First up is details about where we the election happened and what equipment was used
local_precinct_code = Code(code_type = IdentifierType.LOCAL_LEVEL, value = "City of Madison Ward 19")
ward19 = GpUnit(name='Ward 19', gp_type = ReportingUnitType.PRECINCT, id = '_cvr_gp', code=local_precinct_code)
ward19_tabulator = ReportingDevice(id='_rpdev_ward19', model='ESS DS200', notes='Reporting Device used for Madison Ward 19')

# 
# Now we write down where all the details about what contests and candidates were on the ballot. 
# This is separate from the 'CVR' data so it's not repeated in every record
# Note: I think I have the election ID, name, and scope wrong - it's probably supposed to be 'Statewide'
#
fall18_wd9 = Election(id = '_fall_2018_madison_ward_9', name='Fall 2018 Ward 9', election_scope = ward19, contests = [gov_contest, ag_contest, weed_referenda, tax_referenda], candidates = gov_candidates + ag_candidates)

# 
# The CSV included is ~2300 ballots with a whole slug of different offices to be elected.
# We won't try to do every ballot and every office, but we'll pretend we did the first three for two offices
# 269377, 269378, 269379 - dem/dem/gop

# A CVRContest is an actual vote record for a specific office- it refers to the objects we created earlier to get the common data
# So this first object is saying 'This is a vote in the gov contest and it's a vote for Tony Evers'
# Then the second object is saying 'This is a vote in the ag contest and it's a vote for Josh Kaul' 
# Note that they're specific to individual voters - the CVRContest for Gov object (and CVRContesttSelection object) from ballot 239377 is a different 
# object from the CVRContest 
# for Gov for 269378, even though they're both for Evers - they could be marked differently or whatever, so the NIST CVR Standard treats them as different objects
# 
# Add one more fake one where we vote for a write-in for both AG and Gov

cvr377_gov = CVRContest(contest = gov_contest, id = '_cvr_contest_269377_gov', cvr_contest_selection = [CVRContestSelection(contest_selection = evers_selection, id='_cvr269377_cs_gov')])
cvr377_ag = CVRContest(contest = ag_contest, id = '_cvr_contest_269377_ag', cvr_contest_selection = [CVRContestSelection(contest_selection = kaul_selection, id='_cvr269377_cs_ag')])
cvr377_weed = CVRContest(contest = weed_referenda, id = '_cvr_contest_269377_weed', cvr_contest_selection = [CVRContestSelection(contest_selection = weed_yes_selection, id='_cvr269377_cs_weed')])
cvr377_tax = CVRContest(contest = tax_referenda, id = '_cvr_contest_269377_tax', cvr_contest_selection = [CVRContestSelection(contest_selection = tax_yes_selection, id='_cvr269377_cs_tax')])

cvr378_gov = CVRContest(contest = gov_contest, id = '_cvr_contest_269378_gov', cvr_contest_selection = [CVRContestSelection(contest_selection = evers_selection, id='_cvr269378_cs_gov')])
cvr378_ag = CVRContest(contest = ag_contest, id = '_cvr_contest_269378_ag', cvr_contest_selection = [CVRContestSelection(contest_selection = kaul_selection, id='_cvr269378_cs_ag')])
cvr378_weed = CVRContest(contest = weed_referenda, id = '_cvr_contest_269378_weed', cvr_contest_selection = [CVRContestSelection(contest_selection = weed_yes_selection, id='_cvr269378_cs_weed')])
cvr378_tax = CVRContest(contest = tax_referenda, id = '_cvr_contest_269378_tax', cvr_contest_selection = [CVRContestSelection(contest_selection = tax_no_selection, id='_cvr269378_cs_tax')])

cvr379_gov = CVRContest(contest = gov_contest, id = '_cvr_contest_269379_gov', cvr_contest_selection = [CVRContestSelection(contest_selection = walker_selection, id='_cvr269379_cs_gov')])
cvr379_ag = CVRContest(contest= ag_contest, id = '_cvr_contest_269379_ag', cvr_contest_selection = [CVRContestSelection(contest_selection = schimel_selection, id='_cvr269379_cs_ag')])
cvr379_weed = CVRContest(contest = weed_referenda, id = '_cvr_contest_269379_weed', cvr_contest_selection = [CVRContestSelection(contest_selection = weed_yes_selection, id='_cvr269379_cs_weed')])
cvr379_tax = CVRContest(contest = tax_referenda, id = '_cvr_contest_269379_tax', cvr_contest_selection = [CVRContestSelection(contest_selection = tax_no_selection, id='_cvr269379_cs_tax')])

cvr380_gov = CVRContest(contest = gov_contest, id = '_cvr_contest_269380_gov', cvr_contest_selection = [CVRContestSelection(contest_selection = gov_writein_selection, id='_cvr269380_cs_gov')], writeins=1)
cvr380_ag = CVRContest(contest= ag_contest, id = '_cvr_contest_269380_ag', overvotes=1)
#
# Now we put actual ballots together - we take the choices from ballot '377 and bundle them together as a 'Snapshot', and wrap them in a 'CVR'
# Then we do it for ballot '378 and then again for '379. In a real program, we'd combine this step and the previous step as the inner loop
# of something reading from the CSV of the ESS report
# We also need to say what election this is for, which is why we had to create that object before setting up the specific CVR records
#
cvr377 = CVR(id = '_cvr_269377', election=fall18_wd9, cvr_snapshot = [CVRSnapshot(id = '_cvr_snapshot_269377_001', cvr_contests = [cvr377_gov, cvr377_ag, cvr377_weed])])
cvr378 = CVR(id = '_cvr_269378', election=fall18_wd9, cvr_snapshot = [CVRSnapshot(id = '_cvr_snapshot_269378_001', cvr_contests = [cvr378_gov, cvr378_ag])])
cvr379 = CVR(id = '_cvr_269379', election=fall18_wd9, cvr_snapshot = [CVRSnapshot(id = '_cvr_snapshot_269379_001', cvr_contests = [cvr379_gov, cvr379_ag])])
cvr380 = CVR(id = '_cvr_269380', election=fall18_wd9, cvr_snapshot = [CVRSnapshot(id = '_cvr_snapshot_269380_001', cvr_contests = [cvr380_gov, cvr380_ag])])


#
# Finally, put the election metadata together with the ballot-level results and call it a report.
#
fall18_wd9_cvr_report = CastVoteRecordReport(election=fall18_wd9, cvrs = [cvr377, cvr378, cvr379, cvr380], gp_unit = ward19, reporting_device = ward19_tabulator, parties = parties)
fall18_wd9_cvr_report.to_xml()


