import inspect
from mdutils.mdutils import MdUtils
from pipeline_247 import ecog_prep
from classes.ecog import Ecog


class Docs:
    def __init__(self):

        return

    def get_source_code(self, mdFile, fun=None):

        if fun is not None:
            lines = inspect.getsource(fun)
            mdFile.insert_code(lines, language="python")

        return mdFile

    def update_doc_intro(
        self,
        fname,
        title,
        firstline_txt1,
        firstline_lnk,
        firstline_lnk_txt,
        firstline_txt2,
        pipe_code,
    ):

        mdFile = MdUtils(file_name=fname, title=title)

        mdFile.new_line(
            firstline_txt1
            + mdFile.new_inline_link(link=firstline_lnk, text=firstline_lnk_txt)
            + firstline_txt2
        )

        mdFile.new_header(level=1, title="Code Walkthrough")

        # Fetch function from pipeline code
        mdFile = self.get_source_code(mdFile, pipe_code)

        return mdFile

    def update_doc_body(self, mdFile, code_dict):

        for key, value in code_dict.items():
            mdFile.new_header(level=2, title=value["hdr"])
            mdFile.new_line(
                value["desc_txt1"]
                + mdFile.new_inline_link(
                    link=value["desc_lnk"], text=value["desc_lnk_txt"]
                )
            )
            mdFile.insert_code(value["step_code"], language="python")
            mdFile = self.get_source_code(mdFile, value["class_code"])

        return mdFile

    def update_doc_ref(self, mdFile, txt1, lnk):

        mdFile.new_line(txt1 + mdFile.new_inline_link(link=lnk))

        return mdFile

    def create_new_doc(self, step):
        mdFile = self.update_doc_intro(**step["intro_dict"])
        mdFile = self.update_doc_body(mdFile, step["body_dict"])
        mdFile = self.update_doc_ref(mdFile, **step["ref_dict"])

        mdFile.create_md_file()

    ecog = dict(
        [
            (
                "intro_dict",
                dict(
                    [
                        ("fname", "Ecog_preparation"),
                        ("title", "ECoG Preparation"),
                        ("firstline_txt1", "The ecog_prep function in "),
                        ("firstline_lnk", "pipeline_247.py"),
                        ("firstline_lnk_txt", "pipeline_247.py"),
                        (
                            "firstline_txt2",
                            " defines the substeps for preparing ECoG data.",
                        ),
                        ("pipe_code", ecog_prep),
                    ]
                ),
            ),
            (
                "body_dict",
                dict(
                    [
                        (
                            1,
                            dict(
                                [
                                    ("hdr", "Read header from EDF file."),
                                    (
                                        "desc_txt1",
                                        "For more information about EDF headers, see the ",
                                    ),
                                    (
                                        "desc_lnk",
                                        "../../wiki/Data-Descriptions#electrocorticography-ecog",
                                    ),
                                    ("desc_lnk_txt", "Wiki"),
                                    ("step_code", "ecog_file.read_EDFHeader()"),
                                    ("class_code", Ecog.read_EDFHeader),
                                ]
                            ),
                        ),
                        (
                            2,
                            dict(
                                [
                                    ("hdr", "Calculate EDF file end date and time."),
                                    ("desc_txt1", ""),
                                    ("desc_lnk", ""),
                                    ("desc_lnk_txt", ""),
                                    ("step_code", "ecog_file.end_datetime()"),
                                    ("class_code", Ecog.end_datetime),
                                ]
                            ),
                        ),
                        (
                            3,
                            dict(
                                [
                                    ("hdr", "Read electrode data from EDF file."),
                                    (
                                        "desc_txt1",
                                        "Optionally specify start time, end time, and channels to read",
                                    ),
                                    ("desc_lnk", ""),
                                    ("desc_lnk_txt", ""),
                                    (
                                        "step_code",
                                        "ecog_file.read_channels(10, 100000, start=0, end=10)",
                                    ),
                                    ("class_code", Ecog.read_channels),
                                ]
                            ),
                        ),
                        (
                            4,
                            dict(
                                [
                                    ("hdr", "TODO"),
                                    ("desc_txt1", ""),
                                    ("desc_lnk", ""),
                                    ("desc_lnk_txt", ""),
                                    ("step_code", "ecog_file.process_ecog()"),
                                    ("class_code", Ecog.process_ecog),
                                ]
                            ),
                        ),
                        (
                            5,
                            dict(
                                [
                                    (
                                        "hdr",
                                        "Name new EDF file according to the 24/7 naming convention [link]",
                                    ),
                                    ("desc_txt1", ""),
                                    ("desc_lnk", ""),
                                    ("desc_lnk_txt", ""),
                                    (
                                        "step_code",
                                        """ecog_file.name = "".join([ecog_file.sid, "_ecog-raw_", "0", ".edf"])""",
                                    ),
                                    ("class_code", None),
                                ]
                            ),
                        ),
                        (
                            6,
                            dict(
                                [
                                    ("hdr", "Write new EDF file"),
                                    ("desc_txt1", ""),
                                    ("desc_lnk", ""),
                                    ("desc_lnk_txt", ""),
                                    ("step_code", "ecog_file.write_edf()"),
                                    ("class_code", Ecog.write_edf),
                                ]
                            ),
                        ),
                    ]
                ),
            ),
            (
                "ref_dict",
                dict(
                    [
                        ("txt1", "PyEDFlib: "),
                        (
                            "lnk",
                            "https://pyedflib.readthedocs.io/en/latest/ref/highlevel.html",
                        ),
                    ]
                ),
            ),
        ]
    )


# doc_test.create_new_doc(doc_test.ecog)
