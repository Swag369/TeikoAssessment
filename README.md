### Any instructions needed to run your code and reproduce the outputs (We will run your code using GitHub Codespaces).

```
make setup
make pipeline
make dashboard
```

GitHub Codespaces should provide the required environment. If `make` or `python` are not available in the selected Codespaces image, they may need to be installed first.


### An explanation of the schema used for the relational database, with rationale for the design and how this would scale if there were hundreds of projects, thousands of samples and various types of analytics you’d want to perform.

I split up the data based on projects, subjects, sample details, and sample data. The tables for projects, subjects, and samples are straightforward - a project can have many subjects, who can have many samples. Currently, a subject can only belong to a single project, based on the data I was given, but if this is different in the actual domain, this can be altered to support a many to many setup.

Sample data, I didn't keep in a "single row" format, instead melting it because of the format of Q2. This is extensible because different projects with a different data collection than the 5 we currently use would be modeled better instead of every sample needing to have an entry for every unrelated cell-population that SOME other project cares about.

Furthermore for scalability, I have an index on projects within subject - to improve data access at a project level. There is also an index on subject within samples, so I can quickly get data for a subject. Cell count has the primary key of (sample, population) so that it in turn can be quickly accessed. These indexes together support efficient retrieval of any individual row of the initial dataset.

I also have 2 other indexes, that just focuses on the filter criteria for parts 3 and 4.

Further optimizing an indexing strategy would likely be relevant depending on the type of queries the DB sees. I like indexes here because these medical trial workloads would presumably have much more reading volume than write volume, so we benefit more in read performance than we lose in write performance with the inclusion of the index.

### A brief overview of your code structure and an explanation of why you designed it the way you did.

I set up the project structure to mirror the questions. Parts 2, 3, and 4 of the challenge are addressed by the files with the same names.

Part 2, I have a simple window function to get the total counts for a given sample (which I need specifically due to how I set up the schema) - but since the cells have already been unpivoted/melted - my output format easily matches the desired output format.

Part 3, for the first section (boxplots) I just load all the relevant data with SQL, but instead of multiple DB calls for the different groupings (time, response, population) - I did that in memory. I did this because the data fit in-memory for me, and the
```python groups = df.groupby(["time", "population", "response"])["percentage"]```
was effective at splitting up the data how I needed it (because ultimately I only need the percentage series, and I just use the other 3 keys for identification).

For the second part, I knew Welch's t-test and Mann-Whitney tests were the relevant tests for seeing if quantitative datasets were different in a statistically significant way. Using Shapiro-Wilk I couldn't find normality in the data, so I went with the Mann-Whitney U test.

For the dashboard, I kept it minimal and put everything on a single page due to time constraints. Since the instructions mentioned that make pipeline would be run before make dashboard, I used streamlit to just display the precomputed results. This could be vastly improved by having it compute live + caching results when possible, a better customized UI etc - but for the sake of managing scope, i de-prioiritized this.


### A link to the dashboard
https://teikoassessment-jwyycuip2kf9lyanpdr7bh.streamlit.app/ \
http://localhost:8501 <- when locally spinning up
