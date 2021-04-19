function Component()
{}

Component.prototype.createOperationsForArchive = function(archive)
{
	component.addOperation("Extract", archive, "@TargetDir@/Miniconda3/envs/iric/Lib/site-packages");
}
