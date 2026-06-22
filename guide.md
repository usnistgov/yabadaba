# Getting started with yabadaba

This Notebook provides a step-by-step guide for creating a new data project using yabadaba.  

## 1. Decide what schema to use

The first step is to decide what schema to use for representing your data.  This might sound scary and complicated for non-data scientists, but ends up being rather simple when you start building it.

Basic terminology:
- data: The content you wish to capture and save for later.
- metadata: Data fields that are used to characterize other data.  For scientific data, you can think of the primary data being the results, and metadata describing the who, what, where, and how the data was obtained.
- FAIR principles: These are a set of guiding principles for data and databases to "improve the Findability, Accessibility, Interoperability, and Reuse of digital assets".
- format: Data formats dictate how data is organized when saved to a file. Common choices are JSON, XML, YAML, CSV, or a custom .txt file.
- schema: Data schemas map out what values and value types are collected together to represent a full dataset.
- record: This is used by yabadaba both to refer to a Record object as well as a data entry that adheres to a specific schema.


How to design a schema:
1. Think about what data and metadata should be included in the schema.
    1. The general guideline for metadata is to include as much as possible. Essentially, if it is something somebody may wish to know about your data or search for in the future it should be included. Who created it, what were the conditions or input settings, where can more information (i.e. a related publication) be found, how was the data processed and analyzed, ...
    2. Most database infrastructures have a limit on the size of records that can be used.  As such, primary data should be divided between "raw" and "final" data, with the final processed data present in the record, and raw data either in the record if it is small and simple or stored elsewhere if it is large and/or complex. For externally stored raw data, the record can then point to it by listing a file name, url, etc.
    3. What is the data's type, i.e. str, integer, float/real number, list/array...? If the data is complex, can it easily be represented with one or more simple data fields?
 2. Optionally, investigate if there are existing schemas for the same or similar data.
    1. Reusing schemas, schema components, or element naming conventions can help make your schemas easier to build and interpret.
    2. If there is an existing schema, does it capture all the data and metadata you care about or should it be extended/modified?
    3. Do not worry too much if you cannot find an existing schema you like or just want to get started.  In my personal opinion, a specific format and schema are not that important as long as the schema you use contains all the important metadata.
 3. Think about how the data and metadata fields should be organized in the schema. The tree-like data formats like JSON and XML allow for grouping related data fields into subsets. Using subsets allows for more of an object-oriented representation, where you can for instance collect all details and settings for a given instrument or simulation. Subsets also support reuse of the schema components as a single record can repeat a subset or the same subset can be shared by multiple record schemas.

## 2. Define Record classes



