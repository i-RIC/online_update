function Controller()
{
    installer.autoRejectMessageBoxes();
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton);
    })
}

Controller.prototype.IntroductionPageCallback= function()
{
    // click delay here because the next button is initially disabled for ~1 second
    gui.clickButton(buttons.NextButton, 3000);
}

Controller.prototype.DynamicPageCallback= function()
{
    // click delay here because the next button is initially disabled for ~1 second
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.WelcomePageCallback= function()
{
    // click delay here because the next button is initially disabled for ~1 second
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.ComponentSelectionPageCallback= function()
{
    // click delay here because the next button is initially disabled for ~1 second
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.LicenseAgreementPageCallback= function()
{
    gui.currentPageWidget().AcceptLicenseRadioButton.setChecked(true);
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.StartMenuDirectoryPageCallback= function()
{
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.ReadyForInstallationPageCallback= function()
{
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.TargetDirectoryPageCallback = function()
{
    // Keep default at "HomeDir" + "\iRIC_v4"
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.FinishedPageCallback = function()
{
    gui.clickButton(buttons.FinishButton, 1000);
}
