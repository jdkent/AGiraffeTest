#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni

#Generic datagrabber module that wraps around glob in an
io_S3DataGrabber = pe.Node(io.S3DataGrabber(outfields=["outfiles"]), name = 'io_S3DataGrabber')
io_S3DataGrabber.inputs.bucket = 'openneuro'
io_S3DataGrabber.inputs.sort_filelist = True
io_S3DataGrabber.inputs.template = 'sub-[0-9]+/anat/sub-[0-9]+_T1w.nii.gz'
io_S3DataGrabber.inputs.anon = True
io_S3DataGrabber.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
io_S3DataGrabber.inputs.local_directory = '/tmp'

#Wraps command **bet**
fsl_BET = pe.Node(interface = fsl.BET(), name='fsl_BET', iterfield = [''])
fsl_BET.inputs.robust = True

#Generic datasink module to store structured outputs
io_DataSink = pe.Node(interface = io.DataSink(), name='io_DataSink', iterfield = [''])
io_DataSink.inputs.base_directory = '/tmp'

#Wraps command **3dAutoTcorrelate**
afni_AutoTcorrelate = pe.Node(interface = afni.AutoTcorrelate(), name='afni_AutoTcorrelate', iterfield = [''])

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(io_S3DataGrabber, "outfiles", fsl_BET, "in_file")
analysisflow.connect(fsl_BET, "out_file", afni_AutoTcorrelate, "in_file")
analysisflow.connect(afni_AutoTcorrelate, "out_file", io_DataSink, "BET_results")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
