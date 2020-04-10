from dataclasses import dataclass
from typing import List
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom

import datetime
import pytz

# a helper from https://pymotw.com/2/xml/etree/ElementTree/create.html
def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ET.tostring(elem,'unicode')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")


class IdentifierType(Enum):
	FIPS = 'fips'
	LOCAL_LEVEL = 'local-level'
	NATIONAL_LEVEL = 'national-level'
	OCD_ID = 'oci-id'
	STATE_LEVEL = 'state-level'
	OTHER = 'other'

class VoteVariation(Enum):
	N_OF_M = 'n-of-m'


class ReportingUnitType(Enum):
	COMBINED_PRECINCT = 'combined-precinct'
	PRECINCT = 'precinct'

class CVRType(Enum):
	INTERPRETED = 'interpreted'
	MODIFIED = 'modified'
	ORIGINAL = 'original'


@dataclass
class Code:
	label: str = None
	code_type: IdentifierType = None
	other_type: str = None
	value: str = None

	def to_xml(self):
		code_element = ET.Element('Code')
		type_element = ET.SubElement(code_element, 'Type')
		type_element.text = self.code_type.value
		value_element = ET.SubElement(code_element, 'Value')
		value_element.text = self.value

		return code_element

@dataclass
class Party:
	id: str = None
	abbreviation: str = None
	name: str = None

	def to_xml(self):
		party_element = ET.Element('Party')
		party_element.set('ObjectId', self.id)

		abbr_element = ET.SubElement(party_element, 'Abbreviation')
		abbr_element.text = self.abbreviation

		name_element = ET.SubElement(party_element, 'Name')
		name_element.text = self.name
		
		return party_element

@dataclass
class Candidate:
	id: str = None
	name: str = None
	party: Party = None	
	code: Code = None

	def to_xml(self):
		candidate_element = ET.Element('Candidate')
		candidate_element.set('ObjectId', self.id)
		if self.name:
			name_element = ET.SubElement(candidate_element, 'Name')
			name_element.text = self.name	
		if self.party:
			party_id_element = ET.SubElement(candidate_element, 'PartyId')
			party_id_element.text = self.party.id
		return candidate_element

@dataclass
class ContestSelection:
	id: str = None
	code: Code = None
	
	def to_xml(self):
		raise NotImplemented

@dataclass
class CandidateSelection(ContestSelection):
	candidate: Candidate = None
	is_write_in: bool = False

	def to_xml(self):
		candidate_sel_element = ET.Element('ContestSelection')
		candidate_sel_element.set('ObjectId', self.id)
		candidate_sel_element.set('xsi:type', 'CandidateSelection')
		candidate_ids_element = ET.SubElement(candidate_sel_element, 'CandidateIds')
		candidate_ids_element.text = self.candidate.id	
		return candidate_sel_element

@dataclass
class Contest:
	id: str = None
	abbreviation: str = None
	code: Code = None
	name: str = None
	vote_variation: VoteVariation = None
	other_vote_variation: str = None	
	contest_selections: List[ContestSelection] = None
	
	def to_xml(self):
		raise NotImplemented

@dataclass
class CandidateContest(Contest):
	number_elected: int = 1 
	party: Party = None
	votes_allowed: int = 1

	def to_xml(self):
		contest_element = ET.Element('Contest')
		contest_element.set('ObjectId', self.id)
		contest_element.set('xsi:type', 'CandidateContest')

		for sel in self.contest_selections:
			contest_element.append(sel.to_xml())

		contest_name_element = ET.SubElement(contest_element, 'Name')
		contest_name_element.text = self.name 
		if(self.vote_variation):
			vote_variation_element = ET.SubElement(contest_element, 'VoteVariation')
			vote_variation_element.text = self.vote_variation.value

		# I think XML Schema sequences means that this comes at the end?
		number_elected_element = ET.SubElement(contest_element, 'NumberElected')
		number_elected_element.text = '1'
		votes_allowed_element = ET.SubElement(contest_element, 'VotesAllowed')
		votes_allowed_element.text = '1'


		return contest_element

@dataclass
class CVRContestSelection:
	id: str = None
	contest_selection: ContestSelection = None

	def to_xml(self):
		cvr_contest_selection_element = ET.Element('CVRContestSelection')
		cvr_contest_selection_id_element = ET.SubElement(cvr_contest_selection_element, 'ContestSelectionId')
		cvr_contest_selection_id_element.text = self.contest_selection.id

		selection_position_element = ET.SubElement(cvr_contest_selection_element, 'SelectionPosition')
		has_indication_element = ET.SubElement(selection_position_element, 'HasIndication')
		has_indication_element.text = 'yes'
		is_allocable_element = ET.SubElement(selection_position_element, 'IsAllocable')
		is_allocable_element.text = 'yes'
		number_votes_element = ET.SubElement(selection_position_element, 'NumberVotes')
		number_votes_element.text = '1'

		cvr_total_votes_element = ET.SubElement(cvr_contest_selection_element, 'TotalNumberVotes')	
		cvr_total_votes_element.text = '1'

		return cvr_contest_selection_element

@dataclass
class CVRContest:
	id: str = None
	contest: Contest = None
	cvr_contest_selection: List[CVRContestSelection] = None

	def to_xml(self):
		cvr_contest_element = ET.Element('CVRContest')
		cvr_contest_id = ET.SubElement(cvr_contest_element, 'ContestId')
		cvr_contest_id.text = self.contest.id
		if self.cvr_contest_selection:
			for cvr_contest_sel in self.cvr_contest_selection:
				cvr_contest_selection_element = cvr_contest_sel.to_xml()
				cvr_contest_element.append(cvr_contest_selection_element)

		# Todo: dont hardcode this
		cvr_overvotes_element = ET.SubElement(cvr_contest_element, 'Overvotes')	
		cvr_overvotes_element.text = '0'
		cvr_undervotes_element = ET.SubElement(cvr_contest_element, 'Undervotes')	
		cvr_undervotes_element.text = '0'
		cvr_writeins_element = ET.SubElement(cvr_contest_element, 'WriteIns')	
		cvr_writeins_element.text = '0'

		# This is in the PDF but it doesn't seem to be legal
		#cvr_total_votes_element = ET.SubElement(cvr_contest_element, 'TotalNumberVotes')	
		#cvr_total_votes_element.text = '1'

		return cvr_contest_element

@dataclass
class CVRSnapshot:
	id: str = None
	cvr_contests: List[CVRContest] = None

	def to_xml(self):
		cvr_snapshot_element = ET.Element('CVRSnapshot')
		cvr_snapshot_element.set('ObjectId', self.id)
		if self.cvr_contests:
			for cvr_contest in self.cvr_contests:
				cvr_contest_element = cvr_contest.to_xml()
				cvr_snapshot_element.append(cvr_contest_element)

		# TODO - this shouldn't be hardcoded here
		cvr_snapshot_type_element = ET.SubElement(cvr_snapshot_element, 'Type')
		cvr_snapshot_type_element.text = CVRType.ORIGINAL.value
		return cvr_snapshot_element

@dataclass
class GpUnit:
	code: Code = None
	id: str = None
	name: str = None
	gp_type: ReportingUnitType = None
	other_type: str = None

	def to_xml(self):
		gp_unit_element = ET.Element('GpUnit')
		gp_unit_element.set('ObjectId', self.id)		
		if self.code:
			gp_unit_element.append(self.code.to_xml())
		gp_name_element = ET.SubElement(gp_unit_element, 'Name')
		gp_name_element.text = self.name		
		gp_type_element = ET.SubElement(gp_unit_element, 'Type')
		gp_type_element.text = self.gp_type.value

		return gp_unit_element	

@dataclass
class Election:
	id: str = None
	code: IdentifierType = None
	name: str = None
	candidates: List[Candidate] = None
	contests: List[Contest] = None
	election_scope: GpUnit = None
	
	def to_xml(self):
		election_element = ET.Element('Election')
		election_element.set('ObjectId', self.id)

		for candidate in self.candidates:
			election_element.append(candidate.to_xml())
		for contest in self.contests:
			election_element.append(contest.to_xml())

		#election_element.append(self.election_scope.to_xml())
		election_scope_id_element = ET.SubElement(election_element, 'ElectionScopeId')
		election_scope_id_element.text = self.election_scope.id

		return election_element

@dataclass
class CVR:
	id: str = None
	cvr_snapshot: List[CVRSnapshot] = None	
	election: Election = None
	
	def to_xml(self):
		cvr_element = ET.Element('CVR')
		cvr_snapshot_id = ET.SubElement(cvr_element, 'CurrentSnapshotId')
		cvr_snapshot_id.text = self.cvr_snapshot[0].id
		if self.cvr_snapshot:
			cvr_snapshot_element = self.cvr_snapshot[0].to_xml()
			cvr_element.append(cvr_snapshot_element)
		cvr_election_id_element = ET.SubElement(cvr_element, 'ElectionId')
		cvr_election_id_element.text = self.election.id	
		cvr_unique_id_element = ET.SubElement(cvr_element, 'UniqueId')
		cvr_unique_id_element.text = self.id
		return cvr_element

@dataclass
class ReportingDevice:
	id: str = None
	model: str = None
	notes: str = None

	def to_xml(self):
		reporting_device_element = ET.Element('ReportingDevice')
		reporting_device_element.set('ObjectId', self.id)
		if self.model:
			reporting_device_model_element = ET.SubElement(reporting_device_element, 'Model')
			reporting_device_model_element.text = self.model
		if self.notes:
			reporting_device_notes_element = ET.SubElement(reporting_device_element, 'Notes')
			reporting_device_notes_element.text = self.notes

		return reporting_device_element



@dataclass
class CastVoteRecordReport:
	cvrs: List[CVR] = None
	election: List[Election] = None
	generatedDate: str = None
	gp_unit: GpUnit = None
	notes: str = None
	parties: List[Party] = None
	version: str = '1.0.0'
	reporting_device: ReportingDevice = None

	def to_xml(self):
		cvr_data = []
		election_data = self.election.to_xml()
		cvr_report = ET.Element('CastVoteRecordReport')
		cvr_report.set("xmlns", "NIST_V0_cast_vote_records.xsd")
		cvr_report.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
		for cvr in self.cvrs:
			cvr_report.append(cvr.to_xml())

		election_element = self.election.to_xml()
		cvr_report.append(election_element)

		generated_date_element = ET.SubElement(cvr_report, 'GeneratedDate')
		generated_date_element.text = datetime.datetime.now(pytz.utc).isoformat()

		gpunit_element = self.gp_unit.to_xml()
		cvr_report.append(gpunit_element)

		for party in self.parties:
			cvr_report.append(party.to_xml())


		report_generating_device_ids_element = ET.SubElement(cvr_report, 'ReportGeneratingDeviceIds')
		report_generating_device_ids_element.text = self.reporting_device.id 

		reporting_device_element = self.reporting_device.to_xml()
		cvr_report.append(reporting_device_element)

		version_element = ET.SubElement(cvr_report, 'Version')
		version_element.text = self.version

		print(prettify(cvr_report))
		#print(cvr_data)
		#print(election_data)
		#print("footer")
