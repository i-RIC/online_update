function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
	// call default implementation to actually install files
	component.createOperations();

	component.addOperation("Execute", "@TargetDir@/miniconda_install.bat", "@TargetDir@", "@TargetDir@\\Miniconda3", "UNDOEXECUTE", "@TargetDir@/miniconda_uninstall.bat", "@TargetDir@\\Miniconda3");

	component.addOperation("Delete", "@TargetDir@/Miniconda3-py38_4.9.2-Windows-x86_64.exe");

	component.addOperation("SimpleMoveFile", "@TargetDir@/_iric.pyd", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/_iric.pyd");
	component.addOperation("SimpleMoveFile", "@TargetDir@/hdf5.dll", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/hdf5.dll");
	component.addOperation("SimpleMoveFile", "@TargetDir@/iric.py", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/iric.py");
	component.addOperation("SimpleMoveFile", "@TargetDir@/iriclib.dll", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/iriclib.dll");
	component.addOperation("SimpleMoveFile", "@TargetDir@/szip.dll", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/szip.dll");
	component.addOperation("SimpleMoveFile", "@TargetDir@/zlib.dll", "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages/zlib.dll");
}
