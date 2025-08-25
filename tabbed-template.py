import json
import requests
from nicegui import ui
from datetime import datetime
import os

@ui.page('/')
def main():
    tabs = ui.tabs().classes('w-full')
    with tabs:
        ui.tab('Tab 1')
        ui.tab('Tab 2')
        ui.tab('Tab 3')
        ui.tab('Tab 4')
        ui.tab('Tab 5')
        ui.tab('Tab 6')
    panels = ui.tab_panels(tabs, value='Tab 1').classes('w-full')
    with panels:
        with ui.tab_panel('Tab 1'):
            ui.label('Content for Tab 1')
        with ui.tab_panel('Tab 2'):
            ui.label('Content for Tab 2')
        with ui.tab_panel('Tab 3'):
            ui.label('Content for Tab 3')
        with ui.tab_panel('Tab 4'):
            ui.label('Coming soon')
        with ui.tab_panel('Tab 5'):
            ui.label('Coming soon')
        with ui.tab_panel('Tab 6'):
            ui.label('Coming soon')

ui.run()
