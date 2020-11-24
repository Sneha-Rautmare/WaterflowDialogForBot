# https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-dialog-manage-conversation-flow?view=azure-bot-service-4.0&tabs=python

from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,NumberPrompt,PromptOptions, PromptValidatorContext

class BotDialog(ActivityHandler):
    def __init__(self, conversation:ConversationState):
        self.con_statea = conversation
        self.state_prop = self.con_statea.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)
        self.dialog_set.add(TextPrompt("text_prompt", self.isValidRepCommand))
        self.dialog_set.add(NumberPrompt("number_prompt", self.isValidRepCommand))
        # main Waterfall dialog flow to understand the sequence of dialogs
        self.dialog_set.add(WaterfallDialog("main_dialog",[self.GetStartCommand,self.GetReporterId, self.Completed]))

    # check if User entered valid "start" command
    # not using this function for now.
    async def isValidStartCommand(self, prompt_valid:PromptValidatorContext):
        if(prompt_valid.recognized.succeeded is False):
            await prompt_valid.context.send_activity("Please enter start command")
            return False
        else:
            value = str(prompt_valid.recognized.value)
            if value != "start":
                await prompt_valid.context.send_activity("Please enter valid start command")
                return False
        return 
        
    # Check if user enters correct information (start command and reporter-id)
    async def isValidRepCommand(self, prompt_valid :PromptValidatorContext):
        if(prompt_valid.recognized.succeeded is False):
            await prompt_valid.context.send_activity("Please enter reporter ID")
            return False
        else:
            value = str(prompt_valid.recognized.value)
            # sample list created for checking valid reporter-id
            if value not in ["11460fcdb6", "2be81fc57e", "d6ed821f2c","start"] :
                await prompt_valid.context.send_activity("Invalid Reporter ID. Please enter valid reporter ID")
                return False
        return True
        
    async def GetStartCommand(self,waterfall_step:WaterfallStepContext):
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text("Please enter the start command")))

    async def GetReporterId(self,waterfall_step:WaterfallStepContext):
        name = waterfall_step._turn_context.activity.text
        waterfall_step.values["name"] = name
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text("Please enter the reporter ID")))
        
    async def Completed(self,waterfall_step:WaterfallStepContext):
        mobile = waterfall_step._turn_context.activity.text
        waterfall_step.values["reporter_id"] = mobile
        name = waterfall_step.values["name"]
        mobile = waterfall_step.values["reporter_id"]
        profileinfo = f"{mobile} is a valid Reporter ID."
        # return message stating valid reporter-id
        await waterfall_step._turn_context.send_activity(profileinfo)
        return await waterfall_step.end_dialog()
        
    async def on_turn(self,turn_context:TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if(dialog_context.active_dialog is not None):
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")
        
        await self.con_statea.save_changes(turn_context)
    