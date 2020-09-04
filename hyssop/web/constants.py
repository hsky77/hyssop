# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: September 4th 2020 14:12:07 pm
'''

from .. import Module_Path

Hyssop_Folder = Module_Path

KB = 1024
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB

# reserved folder names
Component_Module_Folder = 'component'
Controller_Module_Folder = 'controller'
Unittest_Module_Folder = 'unit_test'
Dependency_Folder = 'dependency'

# reserved file names
Localization_File = 'local.csv'
Hyssop_Web_Config_File = 'server_config.yaml'
Hyssop_Web_Pack_File = 'pack.yaml'
Hyssop_Web_Requirement_File = 'requirements.txt'

# server
LocalCode_Application_Closing = 100
LocalCode_Application_Closed = 101
LocalCode_Not_Subclass = 102
LocalCode_File_Not_Found = 124

# server config
LocalCode_Parameter_Required = 110
LocalCode_Parameter_Type_Error = 111
LocalCode_Setup_Error = 112
LocalCode_Invalid_Parameter = 113
LocalCode_Copied_Name_Equal_To_Origin = 114

# components
LocalCode_Component_Duplicated_Key = 120
LocalCode_Failed_To_Load_Component = 121
LocalCode_Component_Type_Not_Exist = 122

# controllers' localization code
LocalCode_Failed_To_Load_Controller = 130

# controller
LocalCode_Missing_Required_Parameter = 140
LocalCode_Upload_Success = 141

LocalCode_Connect_Failed = 150
