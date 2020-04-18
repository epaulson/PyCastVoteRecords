# CastVoteRecord in Python

This is the beginnings of a Python package to work with elections results in a the [NIST Cast Vote Record Common Data Format](https://pages.nist.gov/CastVoteRecords/). It uses data classes and type hints, so you're probably best off in Python 3.7 or later. The license is BSD.

For now, the library uses only standard library functions, but the validate.py program (which will be part of the test suite) uses lxml to validate an XML Schema. 

The static_cvr.py example is very simple and is just meant to verify that I'm interpreting the format correctly, by hand-constructing a CVR and then serializing it. It takes no arguments and the results of a sample run are in handbuilt.xml. That file valdidates with the NIST XSD file, which is copied right out of the NIST Github repo.

Included in this repo is a CSV of the votes as recorded by the tabulating machine at Ward 9 (where I live) of the City of Madison in the Fall 2018 General Election. The Dane County Clerk puts out this data after elections in [Election Audit Central](https://elections.countyofdane.com/Election-Auditing), I downloaded the Excel spreadsheet, imported the full set into SQLite, and then dumped Ward 9 from SQLite into the CSV file. The data is an export from ESS DS200 tabulating machines, which scan a paper ballot, and then ESS ElectionWare aggregates all of the scans and exports the TIFF image files as well as a set of Excel Spreadsheets of the CVRs. Note that the Excel spreadsheets were the union of everything on the ballot across Dane County, whereas the included CSV filters out only results that came from the City of Madison Ward 9, so there are a lot of NULLs in the CSV and most columns aren't used. 

convert_to_cvr.py reads from this file and spits out a NIST CVR. Note that it only converts the Gov's race, the AG race, and the two referenda. By default it only does the first 10 rows, which is enough to get an undervote, but you can run it with --all to have it spit out a 4.6MB result file, which includes undervotes, overvotes, and writeins (not the actual writein, though - the ESS report doesn't include what was written in, only that there was a writein)

Later comes reading a CVR report. The big questions are what data structures would anyone want after reading the file, and depending on how big the CVR reports get, can one get away with basic, single pass, in-memory XML parsing?

## Questions
* Are CVR Snapshot IDs globally unique, or just unique within a CVR element?
* This is usually easy to figure out from common sense/the examples, but whever the spec says 'reference' or 'link' to an different object, that's always encoded as 'OBJECT_TYPE' with 'Id' concatenated onto it? It would be nice if the PDF spec was more specific about this and the names, without having to go read the XSD file. 
* The spec says "ContestSelection contains one attribute, Code, that can be used to identify the contest selection and thereby eliminate the need to identify it using the subclasses." - but the example files don't a 'Code' in the ContestSelection element
* Why does CVRContest have a status for Overvote and Undervote, and a count for overvotes and undervotes and writeins (but no status for writeins?) 
* The example_1.xml sample file includes an example of a writein in a SelectionPosition, but the CVRContestSelection doesn't link to a ContestSelection
* The basic example in section 5.2 of the spec includes a 'cdf:Position' element in the CVRContestSelection element, but the spec seems to call that OptionPosition?
* The basic example in section 5.2 includes a 'TotalNumberVotes' in the CVRContest (as well as in the CVRContestSelection element) but that doesn't appear to be legal.
* Could the XML Schema not use sequence, which seems to force ordering in the XML entities? It's not a huge deal and if it's a limitation of XML Schema I guess whatetver, but it was annoying to have to go back and reorder elements in the serialization. 
* ReportGeneratingDeviceIds in example_2.xml looks wrong - it's pointing at an election?
* The description of Party in CastVoteRecordReport suggests that you're only supposed to use it for a primary, but is it OK to use in the general too?
* What is the purpose of 'value' in a Code type?
* Why is code in both candidate and contest?
