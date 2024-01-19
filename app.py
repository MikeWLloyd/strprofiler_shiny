import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

import pandas as pd
from pathlib import Path
from math import nan
from collections import OrderedDict

import strprofiler as sp
from calc_functions import single_query, batch_query, file_query

from datetime import date
import time

www_dir = Path(__file__).parent / "www"

reset_count = 0
res_click = 0
res_click_batch = 0
res_click_file = 0

str_database = sp.str_ingress(
    [Path(__file__).parent / "www/jax_database.csv"],
    sample_col="Sample",
    marker_col="Marker",
    sample_map=None,
    penta_fix=True,
).to_dict(orient="index")

html_path = str(Path(__file__).parent / "help.html")

#########
app_ui = ui.page_navbar(
    shinyswatch.theme.superhero(),
    ui.nav_panel(
        "Database Query",
        ui.layout_sidebar(
            ui.panel_sidebar(
                {"id": "sidebar"},
                ui.tags.h3("Search"),
                ui.input_action_button("search", "Search", class_="btn-success"),
                ui.tags.hr(),
                ui.tags.h3("Options"),
                ui.input_checkbox("score_amel_query", "Score Amelogenin", value = True),
                ui.input_numeric("mix_threshold_query", "'Mixed' Sample Threshold", value=3, width = '52%'),
                ui.tags.hr(),
                ui.tags.h3("Example"),
                ui.input_action_button("demo_data", "Load Example Data", class_="btn-primary"),
                ui.tags.hr(),
            position="right"),
            ui.panel_main(
                ui.card(
                    ui.tags.h3("Sample Input"),
                    ui.card(
                        ui.column(12,
                            ui.row(
                                ui.column(3, ui.input_text("marker_1", "Amelogenin", placeholder="")),
                                ui.column(3, ui.input_text("marker_2", "CSF1PO", placeholder="")),
                                ui.column(3, ui.input_text("marker_3", "D2S1338", placeholder="")),
                                ui.column(3, ui.input_text("marker_4", "D3S1358", placeholder="")),
                            ),
                            ui.row(
                                ui.column(3, ui.input_text("marker_5", "D5S818", placeholder="")),
                                ui.column(3, ui.input_text("marker_6", "D7S820", placeholder="")),
                                ui.column(3, ui.input_text("marker_7", "D8S1179", placeholder="")),
                                ui.column(3, ui.input_text("marker_8", "D13S317", placeholder="")),
                            ),
                            ui.row(
                                ui.column(3, ui.input_text("marker_9", "D16S539", placeholder="")),
                                ui.column(3, ui.input_text("marker_10", "D18S51", placeholder="")),
                                ui.column(3, ui.input_text("marker_11", "D19S433", placeholder="")),
                                ui.column(3, ui.input_text("marker_12", "D21S11", placeholder="")),
                            ),
                            ui.row(
                                ui.column(3, ui.input_text("marker_13", "FGA", placeholder="")),
                                ui.column(3, ui.input_text("marker_14", "Penta D", placeholder="")),
                                ui.column(3, ui.input_text("marker_15", "Penta E", placeholder="")),
                                ui.column(3, ui.input_text("marker_16", "TH01", placeholder="")),
                            ),
                            ui.row(
                                ui.column(3, ui.input_text("marker_17", "TPOX", placeholder="")),
                                ui.column(3, ui.input_text("marker_18", "vWA", placeholder="")),
                                # ui.column(3, ui.input_text("marker_19", "Mark", placeholder="")),
                                # ui.column(3, ui.input_text("marker_20", "Mark", placeholder="")),
                            ),
                        ),
                        ui.output_ui("demo_text", class_="blockquote"),
                        full_screen = False, fill = False
                    ),
                ),

            ),
        ),
        ui.card(
            ui.row(
                ui.column(3, ui.tags.h3("Results")),
                ui.column(6, ui.p('')),
                ui.column(3, ui.input_action_button("reset", "Reset Inputs / Results", class_="btn-danger")),
            ),
            ui.column(12,
                {"id": "res_card"},
                ui.output_data_frame("out_result"),
            ),
            full_screen = False, fill = False
        ),
    ),
    ui.nav_panel("Batch Database Query",
        ui.layout_sidebar(
            ui.panel_sidebar(
                {"id": "batch_sidebar"},
                ui.tags.h3("Inputs"),
                ui.tags.hr(),
                ui.input_file("file1", "CSV Input File:", accept=[".csv"], multiple=False, width = '100%'),
                ui.input_action_button("csv_query", "CSV Query", class_="btn-primary", width = '100%'),
                ui.tags.hr(),
                ui.download_button("example_file1", "Download Example Batch File", class_="btn-secondary", width = '100%'),
                ui.tags.hr(),
                ui.tags.h5("Options"),
                ui.input_checkbox("score_amel_batch", "Score Amelogenin", value = True),
                ui.input_numeric("mix_threshold_batch", "'Mixed' Sample Threshold", value=3, width = '75%'),
                ui.input_numeric("tan_threshold_batch", "Tanabe Filter Threshold", value=80, width = '75%'),
                ui.input_numeric("mas_q_threshold_batch", "Masters (vs. query) Filter Threshold", value=80, width = '75%'),
                ui.input_numeric("mas_r_threshold_batch", "Masters (vs. reference) Filter Threshold", value=80, width = '75%'),
                position = "left"
            ),
            ui.panel_main(
                ui.card(
                    ui.row(
                        ui.column(3, ui.tags.h3("Results")),
                        ui.column(6, ui.p('')),
                    ),
                    ui.column(12,
                        {"id": "res_card_batch"},
                        ui.output_data_frame("out_batch_df"),
                        ui.p('')
                    ),
                )
            ) 
        ),
    ),
    ui.nav_panel("File Query",
        ui.layout_sidebar(
            ui.panel_sidebar(
                {"id": "novel_query_sidebar"},
                ui.tags.h3("Inputs"),
                ui.tags.hr(),
                ui.input_file("file2", "CSV Input File:", accept=[".csv"], multiple=False, width = '100%'),
                ui.input_action_button("csv_query2", "CSV Query", class_="btn-primary", width = '100%'),
                ui.tags.hr(),
                ui.download_button("example_file2", "Download Example Batch File", class_="btn-secondary", width = '100%'),
                ui.tags.hr(),
                ui.tags.h5("Options"),
                ui.input_checkbox("score_amel_file", "Score Amelogenin", value = True),
                ui.input_numeric("mix_threshold_file", "'Mixed' Sample Threshold", value=3, width = '75%'),
                ui.input_numeric("tan_threshold_file", "Tanabe Filter Threshold", value=80, width = '75%'),
                ui.input_numeric("mas_q_threshold_file", "Masters (vs. query) Filter Threshold", value=80, width = '75%'),
                ui.input_numeric("mas_r_threshold_file", "Masters (vs. reference) Filter Threshold", value=80, width = '75%'),
                position = "left"
            ),
            ui.panel_main(
                ui.card(
                    ui.row(
                        ui.column(3, ui.tags.h3("Results")),
                        ui.column(6, ui.p('')),
                    ),
                    ui.column(12,
                        {"id": "res_card_file"},
                        ui.output_data_frame("out_file_df"),
                        ui.p('')
                    ),
                )
            ) 
        ),
    ),
    ui.nav_panel("About",
        ui.panel_main(
            ui.tags.iframe(src = 'help.html',
                           width = "100%",
                           style="height: 85vh;",
                           scrolling = 'yes',
                           frameborder="0")
        )
    ),
    title="PDX STR Similarity",
)

########
def server(input, output, session):

################
# Single sample query section
    
    ## Dealing with demo data load
    ### Add some demo genotype information to the fields
    @reactive.Effect
    @reactive.event(input.demo_data)
    def _():
        ui.update_text("marker_1", value="X,Y")
        ui.update_text("marker_2", value="10")
        ui.update_text("marker_3", value="26")
        ui.update_text("marker_4", value="17,18")
        ui.update_text("marker_5", value="12")
        ui.update_text("marker_6", value="8,10")
        ui.update_text("marker_7", value="11,14")
        ui.update_text("marker_8", value="11")
        ui.update_text("marker_9", value="9,11")
        ui.update_text("marker_10", value="12")
        ui.update_text("marker_11", value="13,15")
        ui.update_text("marker_12", value="28,31.2")
        ui.update_text("marker_13", value="21,22")
        ui.update_text("marker_14", value="")
        ui.update_text("marker_15", value="")
        ui.update_text("marker_16", value="7,8")
        ui.update_text("marker_17", value="8,11")
        ui.update_text("marker_18", value="16,18")
        @output
        @render.text
        def demo_text():
            x = ui.strong('Demo Data from sample: J000077608F001_P0')
            return x
    

    ## Reset all marker fields
    ### Effect occurs on click of 'Reset Inputs' button
    @reactive.Effect
    @reactive.event(input.reset)
    def reset_clicked():
        ui.update_text("marker_1", value="")
        ui.update_text("marker_2", value="")
        ui.update_text("marker_3", value="")
        ui.update_text("marker_4", value="")
        ui.update_text("marker_5", value="")
        ui.update_text("marker_6", value="")
        ui.update_text("marker_7", value="")
        ui.update_text("marker_8", value="")
        ui.update_text("marker_9", value="")
        ui.update_text("marker_10", value="")
        ui.update_text("marker_11", value="")
        ui.update_text("marker_12", value="")
        ui.update_text("marker_13", value="")
        ui.update_text("marker_14", value="")
        ui.update_text("marker_15", value="")
        ui.update_text("marker_16", value="")
        ui.update_text("marker_17", value="")
        ui.update_text("marker_18", value="")
        ui.update_text("marker_19", value="")
        ui.update_text("marker_20", value="")
        ui.update_checkbox("score_amel_query", value=True)
        ui.update_numeric("mix_threshold_query", value='3')
        @output
        @render.text
        def demo_text():
            x = ui.strong('')
            return x

    ## Dealing with calculating a results rtable
    ### Catch when either reset or search is clicked
    ### If reset, clear the query and run to make an empty df.
    ### The empty df removes any existing table from the UI.
    ### If search, populate with the query table, check if something
    ### is actually in query, and then run single_query
    ### If query has data, results are expected and 
    ### the download button is turned on. If query is empty, 
    ### no results are expected and download button removed. 
    @reactive.Calc
    @reactive.event(input.search, input.reset)
    def output_results():
        global reset_count
        global res_click

        if (input.reset() != reset_count):
            query = {
                "Amelogenin": '', 
                "CSF1PO": '', 
                "D2S1338": '', 
                "D3S1358": '', 
                "D5S818": '', 
                "D7S820": '', 
                "D8S1179": '', 
                "D13S317": '', 
                "D16S539": '', 
                "D18S51": '', 
                "D19S433": '', 
                "D21S11": '', 
                "FGA": '', 
                "PentaD": '', 
                "PentaE": '', 
                "TH01": '', 
                "TPOX": '', 
                "vWA": '',
            }
        else:
            query = {
                "Amelogenin": input.marker_1(), 
                "CSF1PO": input.marker_2(), 
                "D2S1338": input.marker_3(), 
                "D3S1358": input.marker_4(), 
                "D5S818": input.marker_5(), 
                "D7S820": input.marker_6(), 
                "D8S1179": input.marker_7(), 
                "D13S317": input.marker_8(), 
                "D16S539": input.marker_9(), 
                "D18S51": input.marker_10(), 
                "D19S433": input.marker_11(), 
                "D21S11": input.marker_12(), 
                "FGA": input.marker_13(), 
                "PentaD": input.marker_14(), 
                "PentaE": input.marker_15(), 
                "TH01": input.marker_16(), 
                "TPOX": input.marker_17(), 
                "vWA": input.marker_18(),
            }
        reset_count = input.reset()
        if not any(query.values()):
            @output
            @render.text
            def demo_text():
                return('')
            ui.remove_ui("#inserted-downloader")
            ui.remove_ui("#inserted-switch")
            res_click = 0
            return None
        if (res_click == 0):
            ui.insert_ui(
                ui.div({"id": "inserted-downloader"}, ui.download_button("download", "Download CSV", width = '25%', class_="btn-primary")),
                selector="#res_card",
                where="afterEnd",
            )
            ui.insert_ui(
                ui.div({"id": "inserted-switch"}, ui.input_switch("filters", "Data Filters", False)),
                selector="#res_card",
                where="beforeBegin",
            )           
            res_click = 1

        return single_query(query, str_database, input.score_amel_query(), input.mix_threshold_query())

    ## Dealing with making a dataframe for display
    @output
    @render.data_frame
    def out_result():
        output_df = output_results()
        if output_df is not None:
            return render.DataGrid(output_df, filters=input.filters(), height = 350)

    ## Dealing with dowloading results, when requested. 
    ## Note that output_results() is a reactive Calc result. 
    @session.download(filename='PDX_STR_Query_Results_'+date.today().isoformat()+'-'+time.strftime("%Hh-%Mm", time.localtime())+'.csv')
    def download():
        if output_results() is not None:
            yield output_results().to_csv()

################

################
# CSV BATCH SECTION

    ### On click of CSV Query, load file (or catch empty)
    ### This effect catches any Calc change below (file loaded or not) 
    ### and if present uses the query DF as input to batch query. 
    ### Results are saved out to a file. 
    @output
    @render.data_frame
    def out_batch_df():
        output_df = batch_query_results()
        if output_df is not None:
            return render.DataTable(output_df)

    ### File input loading
    @reactive.Calc
    @reactive.event(input.csv_query)
    def batch_query_results():
        global res_click_file
        file: list[FileInfo] | None = input.file1()
        if file is None:
            ui.remove_ui("#inserted-downloader2")
            return pd.DataFrame({'' : []})
        query_df = sp.str_ingress(
            [file[0]["datapath"]],
            sample_col="Sample",
            marker_col="Marker",
            sample_map=None,
            penta_fix=True,
        ).to_dict(orient="index")
        
        if (res_click_file == 0):
            ui.insert_ui(
                ui.div({"id": "inserted-downloader2"}, ui.download_button("download2", "Download CSV", width = '25%', class_="btn-primary")),
                selector="#res_card_batch",
                where="beforeEnd",
            )
            res_click_file = 1
        return batch_query(query_df, str_database, input.score_amel_batch(), input.mix_threshold_batch(), input.tan_threshold_batch(), input.mas_q_threshold_batch(), input.mas_r_threshold_batch())

    ## Dealing with dowloading results, when requested. 
    ## Note that output_results() is a reactive Calc result. 
    @session.download(filename='PDX_STR_Batch_Results_'+date.today().isoformat()+'_'+time.strftime("%Hh-%Mm", time.localtime())+'.csv')
    def download2():
        if batch_query_results() is not None:
            yield batch_query_results().to_csv()

    ## Dealing with passing example file to user. 
    @session.download()
    def example_file1():
        path = "www/Example_Batch_File.csv"
        return str(path)
    
################   
# File many to many query    
    
    ### On click of CSV Query, load file (or catch empty)
    ### This effect catches any Calc change below (file loaded or not) 
    ### and if present uses the query DF as input to batch query. 
    ### Results are saved out to a file. 
    @output
    @render.data_frame
    def out_file_df():
        output_df = file_query_results()
        if output_df is not None:
            return render.DataTable(output_df)

    ### File input loading
    @reactive.Calc
    @reactive.event(input.csv_query2)
    def file_query_results():
        global res_click_batch
        file: list[FileInfo] | None = input.file2()
        if file is None:
            ui.remove_ui("#inserted-downloader3")
            return pd.DataFrame({'' : []})
        query_df = sp.str_ingress(
            [file[0]["datapath"]],
            sample_col="Sample",
            marker_col="Marker",
            sample_map=None,
            penta_fix=True,
        ).to_dict(orient="index")
        
        if (res_click_batch == 0):
            ui.insert_ui(
                ui.div({"id": "inserted-downloader3"}, ui.download_button("download3", "Download CSV", width = '25%', class_="btn-primary")),
                selector="#res_card_file",
                where="beforeEnd",
            )
            res_click_batch = 1
        return file_query(query_df, input.score_amel_file(), input.mix_threshold_file(), input.tan_threshold_file(), input.mas_q_threshold_file(), input.mas_r_threshold_file())

    ## Dealing with dowloading results, when requested. 
    ## Note that output_results() is a reactive Calc result. 
    @session.download(filename='PDX_STR_Results_'+date.today().isoformat()+'_'+time.strftime("%Hh-%Mm", time.localtime())+'.csv')
    def download3():
        if file_query_results() is not None:
            yield file_query_results().to_csv()

    ## Dealing with passing example file to user. 
    @session.download()
    def example_file2():
        path = "www/Example_Batch_File.csv"
        return str(path)
    
    
    

# "marker_1", "Amelogenin"
# "marker_2", "CSF1PO"
# "marker_3", "D2S1338"
# "marker_4", "D3S1358"
# "marker_5", "D5S818"
# "marker_6", "D7S820"
# "marker_7", "D8S1179"
# "marker_8", "D13S317"
# "marker_9", "D16S539"
# "marker_10", "D18S51"
# "marker_11", "D19S433"
# "marker_12", "D21S11"
# "marker_13", "FGA"
# "marker_14", "Penta D"
# "marker_15", "Penta E"
# "marker_16", "TH01"
# "marker_17", "TPOX"
# "marker_18", "vWA"
# "marker_19", "Marker 19"
# "marker_20", "Marker 20"


app = App(app_ui, server, static_assets = www_dir)