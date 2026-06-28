from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.spinner import MDSpinner
from kivy.utils import get_color_from_hex
from utils.constants import COLOR_PRIMARY_GREEN
from documents.pdf_extractor import PDFExtractor
from documents.chunker import DocumentChunker
from summarizers.factory import SummarizerFactory
from kivymd.uix.filemanager import MDFileManager
import os
import threading

class PDFScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "pdf_summary"
        self.app = app
        self.selected_file = None
        self.extracted_text = ""

        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Summarize PDF",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        content = MDBoxLayout(orientation="vertical", padding="20dp", spacing="20dp")

        self.lbl_status = MDLabel(
            text="No file selected.\nNote: Only text-based PDFs are supported offline.",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=0.4
        )
        content.add_widget(self.lbl_status)

        # Select Button
        self.btn_select = MDRaisedButton(
            text="Select PDF File",
            pos_hint={"center_x": .5},
            on_release=self.open_file_manager
        )
        content.add_widget(self.btn_select)

        # File Manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=['.pdf']
        )

        # Action Box
        action_box = MDBoxLayout(orientation="vertical", size_hint_y=0.4, spacing="10dp")
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=("30dp", "30dp"),
            pos_hint={'center_x': .5},
            active=False
        )
        action_box.add_widget(self.spinner)

        self.btn_summarize = MDRaisedButton(
            text="Extract & Summarize",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            pos_hint={"center_x": .5},
            size_hint_x=0.8,
            disabled=True,
            on_release=self.start_processing
        )
        action_box.add_widget(self.btn_summarize)

        content.add_widget(action_box)
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def open_file_manager(self, instance):
        # On Android, might need to start at a specific directory.
        # Fallback to home dir for desktop
        start_path = os.path.expanduser("~")
        self.file_manager.show(start_path)

    def select_path(self, path):
        self.exit_manager()
        self.selected_file = path
        filename = os.path.basename(path)
        self.lbl_status.text = f"Selected: {filename}\nReady to extract."
        self.btn_summarize.disabled = False

    def exit_manager(self, *args):
        self.file_manager.close()

    def start_processing(self, instance):
        if not self.selected_file:
            return

        self.btn_summarize.disabled = True
        self.btn_select.disabled = True
        self.spinner.active = True
        self.toolbar.title = "Processing PDF..."

        threading.Thread(target=self._process_pdf).start()

    def _process_pdf(self):
        try:
            # 1. Extract
            extraction = PDFExtractor.extract_text(self.selected_file)

            if extraction['error']:
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._show_error(extraction['error']))
                return

            text = extraction['text']
            if not text.strip():
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._show_error("Could not extract any text. Image-based PDF?"))
                return

            # 2. Chunking (if needed) & Summarize
            self.app.profiler.start()

            try:
                ratio = float(self.app.settings.get('default_ratio', '0.3'))
                if ratio < 0.05: ratio = 0.05
                if ratio > 0.80: ratio = 0.80
            except ValueError:
                ratio = 0.3

            model_name = self.app.settings.get('default_model', 'Hybrid Green Mode')
            summarizer = SummarizerFactory.get_summarizer(model_name)

            # Simplified chunking logic for MVP: just split, summarize each, and combine
            chunks = DocumentChunker.chunk_text(text, max_words_per_chunk=1000)

            chunk_summaries = []
            total_input_words = 0
            total_output_words = 0

            for chunk in chunks:
                res = summarizer.summarize(chunk, ratio)
                if res.summary_text:
                    chunk_summaries.append(res.summary_text)
                    total_input_words += res.input_word_count
                    total_output_words += res.output_word_count

            final_summary = "\n\n".join(chunk_summaries)

            # Generate final SummaryResult struct manually since we batched
            from storage.models import SummaryResult
            import time
            final_result = SummaryResult(
                summary_text=final_summary,
                model_name=model_name,
                input_word_count=total_input_words,
                output_word_count=total_output_words,
                compression_ratio=total_output_words/total_input_words if total_input_words else 0,
                sentence_count=final_summary.count('.') + final_summary.count('!'),
                keywords=[], # Simplified for chunked
                processing_time_seconds=0 # Replaced by profiler
            )

            batt_cap = float(self.app.settings.get('battery_capacity', '4000'))
            grid_fac = float(self.app.settings.get('grid_factor', '708.2'))
            metrics = self.app.profiler.stop(
                compression_ratio=final_result.compression_ratio,
                output_words=final_result.output_word_count,
                grid_factor=grid_fac,
                capacity_mah=batt_cap
            )
        except Exception as e:
            print(f"Error processing PDF: {e}")
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._show_error(f"Error: {str(e)}"))
            return
        final_result.processing_time_seconds = metrics['duration_seconds']

        # Save History
        from storage.models import HistoryEntry
        entry = HistoryEntry(
            id=None,
            created_at=time.time(),
            input_type='pdf',
            source_name=os.path.basename(self.selected_file),
            model_name=model_name,
            input_word_count=final_result.input_word_count,
            output_word_count=final_result.output_word_count,
            compression_ratio=final_result.compression_ratio,
            summary_text=final_result.summary_text,
            duration_seconds=metrics['duration_seconds'],
            data_used_bytes=metrics['data_used_bytes'],
            battery_delta_percent=metrics['battery_delta_percent'],
            energy_joules=metrics['energy_joules'],
            energy_wh=metrics['energy_wh'],
            carbon_gco2e=metrics['carbon_gco2e'],
            efficiency_score=metrics['efficiency_score']
        )
        self.app.db.add_history(entry)

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._on_complete(final_result, metrics))

    def _show_error(self, err_msg):
        self.spinner.active = False
        self.btn_summarize.disabled = False
        self.btn_select.disabled = False
        self.toolbar.title = "Error"
        self.lbl_status.text = err_msg

    def _on_complete(self, result, metrics):
        self.spinner.active = False
        self.btn_summarize.disabled = False
        self.btn_select.disabled = False
        self.toolbar.title = "Summarize PDF"

        self.app.screens['result'].show_result(result, metrics)
        self.app.switch_screen("result")
