import glob
import os
import argparse
import re
import socket
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from classes.ecog import Ecog
from scipy.io import loadmat

class Plots:

    def __init__(self, config, outname):
        """Initializes the instance based on subject identifier.

        Args:
          sid (str): Identifies subject.
        """

        self.sid = config.sid
        self.filenames = config.filenames
        self.outname = outname

    def arg_parse(self):
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--sid", type=str)
        parser.add_argument("--input_name", nargs="*", default=None)
        parser.add_argument(
            "--steps",
            nargs="*",
            default=["subject_prep", "ecog_prep", "audio_prep", "transcript_prep"],
        )

        args = parser.parse_args()

        return args

    def load_surf(self):
        "load brain surface plot"

        files = [f for f in self.filenames["brain-space"]]
        
        # if one hemisphere
        if len(files) == 1:
            surf1 = loadmat(files[0])
            surf2 = []
        # if both hemispheres
        elif len(files) == 2:
            surf1 = loadmat(files[0])
            surf2 = loadmat(files[1])

        return surf1, surf2

    def read_coor(self, path,id):
        "read electrode coordinates"

        df_coor = pd.DataFrame()
        for sid in id:
            sid_path = os.path.join(path, sid)
            file = os.path.join(sid_path, sid + "-electrode-coordinates.csv")
            df = pd.read_csv(file)
            df['subject'] = sid
            df_coor = df_coor.append(df)

        return df_coor

    def plot_brain(self, surf1, surf2):
        "plot 3D brain"

        # surf["faces"] is an n x 3 matrix of indices into surf["coords"]; connectivity matrix
        # Subtract 1 from every index to convert MATLAB indexing to Python indexing
        surf1["faces"] = np.array([conn_idx - 1 for conn_idx in surf1["faces"]])

        # Plot 3D surfact plot of brain, colored according to depth
        fig = go.Figure()

        fig.add_trace(go.Mesh3d(x=surf1["coords"][:,0], y=surf1["coords"][:,1], z=surf1["coords"][:,2],
                        i=surf1["faces"][:,0], j=surf1["faces"][:,1], k=surf1["faces"][:,2],
                        color='rgb(175,175,175)'))
        
        # if both hemispheres
        if surf2:
            surf2["faces"] = np.array([conn_idx - 1 for conn_idx in surf2["faces"]])

            fig.add_trace(go.Mesh3d(x=surf2["coords"][:,0], y=surf2["coords"][:,1], z=surf2["coords"][:,2],
                            i=surf2["faces"][:,0], j=surf2["faces"][:,1], k=surf2["faces"][:,2],
                            color="rgb(175,175,175)"))

        fig.update_traces(lighting_ambient=0.3)
        return fig

    def plot_electrodes(self, elec_names,X,Y,Z,cbar_title,colorscale):
        "plot 3D electrodes"

        r = 1.5
        fignew = go.Figure()
        for elecname,center_x,center_y,center_z in zip(elec_names,X,Y,Z):
            u, v = np.mgrid[0:2*np.pi:26j, 0:np.pi:26j]
            x = r * np.cos(u)*np.sin(v) + center_x
            y = r * np.sin(u)*np.sin(v) + center_y
            z = r * np.cos(v) + center_z

            fignew.add_trace(go.Surface(x=x,y=y,z=z,surfacecolor=np.ones(shape=z.shape),name=elecname,
                        legendgroup=cbar_title,colorscale=colorscale))
        
        return fignew

    def scale_colorbar(self, fignew, df, cbar_min, cbar_max, cbar_title):
        "Set min/max of colorbar"

        if cbar_min is not None:
            cmin = cbar_min
        else:
            cmin = df["effect"].min()

        if cbar_max is not None:
            cmax = cbar_max
        else:
            cmax = df["effect"].max()
        fignew.update_traces(cmin=cmin,cmax=cmax,colorbar_title=cbar_title,
                            colorbar_title_font_size=40,colorbar_title_side='right')
        
        return fignew
        
    def electrode_colors(self, fignew, df, subset):
        "Color electrodes according to effect"

        # Once max, min of colorbar is set, you can just use the value you want to plot (e.g. correlation) to determine the coloring,
        # must be in array the same shape as z data
        if subset > 0:
            fignew.update_traces(colorbar_x = 1 + 0.2*subset)
        for elec_idx in range(0,len(fignew.data)):
            effect = df["effect"][df.index[df["subject"]+df["name"] == fignew.data[elec_idx]["name"]]].tolist()
            fignew.data[elec_idx]["surfacecolor"] = fignew.data[elec_idx]["surfacecolor"] * effect

        return fignew

    def update_properties(self,fig):

        # Left hemisphere
        # TODO: add camera for other views
        camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=-1.5, y=0, z=0)
        )

        scene = dict(
            xaxis = dict(visible=False),
            yaxis = dict(visible=False),
            zaxis = dict(visible=False),
            aspectmode='auto'
        )

        fig.update_layout(scene_camera=camera,scene=scene)
        fig.update_traces(lighting_specular=0.4,colorbar_thickness=40,colorbar_tickfont_size=30,
                        lighting_roughness=0.4,lightposition=dict(x=0, y=0, z=100))

        return fig

    def main(self,id,effect_file,cbar_titles,outname,cbar_min,cbar_max,colorscales,coor_in_effect_file):
        #id = sys.argv[1]
        #eff_file_name = sys.argv[2]
        main_dir = ""

        if len(id) > 1:
            coor_type = "MNI"
        else:
            coor_type = "T1"

        path = os.path.join(main_dir,"ecog_coordinates")
        
        surf1, surf2 = self.load_surf(path, id)
        fig = plot_brain(surf1, surf2)

        if coor_in_effect_file == 0:
            df_coor = read_coor(path,id)

        for subset, cbar_title in enumerate(cbar_titles):
            
            if colorscales is None:
                colorscale = [[0,'rgb(255,0,0)'], [1,'rgb(255,255,0)']]
            else:
                colorscale = colorscales[cbar_title] 

            eff_file = os.path.join(main_dir + "results/brain_maps/effects/" + effect_file[subset])
            df_eff = pd.read_csv(eff_file)
            df_eff['subject'] = df_eff['subject'].astype("string")

            if 'MNI_X' in df_eff.columns:
                df_coor = df_eff
                fignew = plot_electrodes(df_coor['index'],df_coor[coor_type+"_X"],df_coor[coor_type+"_Y"],df_coor[coor_type+"_Z"],
                    cbar_title,colorscale)
            else:
                # Filter electrodes to plot
                df_coor = df_coor[df_coor.name.isin(df_eff.name)]
                fignew = plot_electrodes(df_coor['subject'] + df_coor['name'],df_coor[coor_type+"_X"],df_coor[coor_type+"_Y"],df_coor[coor_type+"_Z"],
                    cbar_title,colorscale)
                
            fignew = scale_colorbar(fignew, df_eff, cbar_min, cbar_max, cbar_title)
            fignew = electrode_colors(fignew, df_eff, subset)
            
            # Add electrode traces to main figure
            for trace in range(0,len(fignew.data)):
                fig.add_trace(fignew.data[trace])

        fig = update_properties(fig)

        fig.write_image(outname, scale=6, width=1200, height=1000)

        return
    
    def highlight_elec_imgs(self):

        # TI is patient-specific  
        elec_loc = pd.read_csv(next(self.filenames["elec-loc-T1"]))
        surf1, surf2 = self.load_surf()
        fig = self.plot_brain(surf1, surf2)
        breakpoint()
        fignew = self.plot_electrodes(df_coor['index'],df_coor[coor_type+"_X"],df_coor[coor_type+"_Y"],df_coor[coor_type+"_Z"])
        breakpoint()
        
        return
    
    def create_coor_file(self):
        "Combine T1, MNI coordinates, annatomical regions information. Correct any naming discrepencies."

        # T1, patient specific electrode coordinates
        elec_loc_T1 = pd.read_csv(next(self.filenames["elec-loc-T1"]),
                                  delimiter= ' ',
                                  index_col=False,
                                  names=["elec_name","X_T1","Y_T1","Z_T1","elec_type"]
                                  )
        # MNI, average brain space
        elec_loc_MNI = pd.read_csv(next(self.filenames["elec-loc-MNI"]),
                                  delimiter= ' ',
                                  index_col=False,
                                  names=["elec_name","X_MNI","Y_MNI","Z_MNI","elec_type"]
                                  )
        #TODO: Adapt number of percent, region pairs
        #TODO: Sort region based on percent?
        # Anatomical region of each electrode
        elec_region = pd.read_csv(next(self.filenames["elec-region"]),
                                  delimiter=' ',
                                  names=["elec_name","X_T1","Y_T1","Z_T1",
                                         "percent_1","region_1",
                                         "percent_2","region_2",
                                         "percent_3","region_3",
                                         "percent_4","region_4",
                                         "percent_5","region_5"]
                                         )
        elec_summary = elec_region[elec_region.elec_name == "%"]
        elec_region = elec_region[elec_region.elec_name != "%"]
        elec_region[["X_T1","Y_T1","Z_T1"]] = elec_region[["X_T1","Y_T1","Z_T1"]].apply(pd.to_numeric)
        
        # Merge files into one
        elec_loc = elec_loc_T1.merge(elec_loc_MNI,on=["elec_name","elec_type"])
        coor_file = elec_loc.merge(elec_region,on=["elec_name","X_T1","Y_T1","Z_T1"])

        # Validate electrode naming (format to electrode names from EDF header)
        # TODO: Verify electrode name consistency across EDF files
        ecog_file = Ecog(self.sid, str(self.filenames["ecog-raw"]).format(sid=self.sid,part="001"))
        ecog_file.read_EDFHeader()
        valid_names = ecog_file.ecog_hdr["channels"]

        #grp, num, *junk = re.split('(\d+)',elec)
        edf_file_names = pd.DataFrame(valid_names)
        edf_file_names[["lett","num"]] = edf_file_names[0].str.extract('([A-Za-z]+)(\d+\.?\d*)',expand=True)

        # Filter out known non-electrode channels
        edf_file_names = edf_file_names[~edf_file_names["lett"].isin(ecog_file.non_electrode_id)]
        edf_file_names["num"] = pd.to_numeric(edf_file_names["num"])

        coor_file[["lett","num"]] = coor_file.elec_name.str.extract('([A-Za-z]+)(\d+\.?\d*)',expand=True)

        # First check is stripping leading zeros
        coor_file["num"] = pd.to_numeric(coor_file["num"])

        merged_coor_file = pd.DataFrame()
        for grp in edf_file_names["lett"].unique():
            match_edf_file_names = edf_file_names[edf_file_names["lett"] == grp]

            match_coor_file = coor_file[coor_file["lett"] == grp]
            match_coor_file = match_coor_file.merge(match_edf_file_names,on="num",how="right")
            merged_coor_file = pd.concat([merged_coor_file,match_coor_file])
            
        merged_coor_file.drop(["lett_x","lett_y","num"], axis=1, inplace=True)
        column_to_move = merged_coor_file.pop(0)
        merged_coor_file.insert(1, "elec_name_edf", column_to_move )

        merged_coor_file.to_csv(str(self.filenames["coor-file"]).format(sid=self.sid))

        return