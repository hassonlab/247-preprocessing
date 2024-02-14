Documenting the Docs
====================

# How to update and maintain 24/7 documentation

It is important to regularly update the documentation to keep up-to-date with any changes to the pipeline or code!

Documentation is hosted on the Hasson Lab GitHub [link]

You can find important information about the project in the Wiki and the docs folder.

The goals of 24/7 documentation are:
- To clearly document and describe relevant processes and descisions.
- To make processing of 24/7 patients easy for lab members who are new to the pipeline.
- To provide a template for building new pipelines using 24/7 data.

## Code Walk-throughs:
There is a separate Code Walk-through doc for each step in the pipeline, which breaks down the step into sub-steps and provides and explains the relevant code. This is both a step-by-step breakdown of the pipeline, and a place to further explain the code.

Since these docs are dependant on the current code, they should be updated regularly.

Code Walk-throughs are currently updated using update_docs.py

update_docs.py will:
- Format the doc in a uniform way.
- Pull from a dictionary to update the doc contents.

If you need to update the content of class method and nothing else:
1. Run update_docs.py (update_docs will pull the updated content of the class method)

If you need to update a sub-step description, update the name of a class method, add or remove sub-steps, etc.:
1. Manually change this in the relevant dictionary
2. Run update_docs.py