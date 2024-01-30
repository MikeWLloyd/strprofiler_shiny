from shiny import App, render, ui, experimental
import pandas as pd
from shiny_tables import enhanced_from_dataframe
import datetime
import shinyswatch

import pandas as pd

df_test = pd.DataFrame({"AA" : ['A', 'A', 'A,B', 'A,B', 'A,C'],
                   "BB" : [5.0, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14., 3, 6, 2, 14],
                   "E" : [23., 45, 64, 32, 23]}) 

def color_positive_a(val):
    if val != df_test['AA'][0]:
        return {'class': 'table-danger'}

def color_positive_b(val):
    if val != df_test['BB'][0]:
        return {'class': 'table-danger'}

def color_positive_c(val):
    if val != df_test['C'][0]:
        print('here')
        return {'class': 'table-danger'}
    else: 
        print('there')

def color_positive_d(val):
    if val != df_test['D'][0]:
        return {'class': 'table-danger'}

def color_positive_e(val):
    if val != df_test['E'][0]:
        return {'class': 'table-danger'}

cell_style_dict = {
    'AA': color_positive_a,
    'BB': color_positive_b,
    'C': color_positive_c,
    'D': color_positive_d,
    'E': color_positive_e
}

header_style_dict = {
    'AA': {'style': 'width:1500%; color:blue'}
}

# "Amelogenin": '', 
# "CSF1PO": '', 
# "D2S1338": '', 
# "D3S1358": '', 
# "D5S818": '', 
# "D7S820": '', 
# "D8S1179": '', 
# "D13S317": '', 
# "D16S539": '', 
# "D18S51": '', 
# "D19S433": '', 
# "D21S11": '', 
# "FGA": '', 
# "PentaD": '', 
# "PentaE": '', 
# "TH01": '', 
# "TPOX": '', 
# "vWA": '',

print(cell_style_dict)


def wrap_company(row, col_name):
    return ui.tooltip(
        ui.tags.button(row[col_name], ),
        f"This is a tool tip for {row[col_name]} that shows the link {row['Company_HREF']}"
    )


app_ui = ui.page_bootstrap(
    shinyswatch.theme.yeti(),
    ui.panel_title("Demo Bootstrap tables for Shiny Python."),
    ui.row(
        ui.column(6, ui.output_ui("result")),
    )
)

def server(input, output, session):

    @output
    @render.ui
    def result():
        return enhanced_from_dataframe(
            df_test,
            cell_style_dict=cell_style_dict,
            columns=['AA', 'BB', 'C', 'D', 'E'],
            header_style_dict=header_style_dict,
            process_header_styles=True
           )


app = App(app_ui, server)