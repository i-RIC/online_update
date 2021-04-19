function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
	// call default implementation to actually install files
	component.createOperations();

	if (systemInfo.productType === "windows") {
		install_miniconda();
	}
	delete_installer();
}

function install_miniconda()
{
	component.addOperation("Mkdir", "@TargetDir@/Miniconda3")
	component.addOperation("Execute", "@TargetDir@/Miniconda3-py38_4.9.2-Windows-x86_64.exe", "/InstallationType=JustMe", "/RegisterPython=0", "/AddToPath=0", "/S", "/D=@TargetDir@\\Miniconda3");
	component.addOperation("Execute", "@TargetDir@/Miniconda3/condabin/conda.bat", "create", "-p", "@TargetDir@/Miniconda3/envs/iric", "python=3.8", "-y", "-q");
	component.addOperation("Execute", "@TargetDir@/Miniconda3/condabin/conda.bat", "install", "-p", "@TargetDir@/Miniconda3/envs/iric", "numpy", "-y");
}

function delete_installer()
{
	component.addOperation("Delete", "@TargetDir@/Miniconda3-py38_4.9.2-Windows-x86_64.exe");
}
