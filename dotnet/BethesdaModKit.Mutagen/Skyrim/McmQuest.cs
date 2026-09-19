using Mutagen.Bethesda;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Skyrim;

namespace BMK.Mutagen.Skyrim;

public static class McmQuest
{
    public static Quest Add(SkyrimMod mod, McmQuestOptions options)
    {
        var quest = mod.Quests.AddNew(options.EditorId);
        quest.Name = options.DisplayName;
        quest.Flags = Quest.Flag.StartGameEnabled | Quest.Flag.RunOnce;
        quest.VirtualMachineAdapter = new QuestAdapter
        {
            Version = 5,
            ExtraBindDataVersion = 2,
            FileName = string.Empty,
        };
        var script = new ScriptEntry
        {
            Name = options.ConfigScriptName,
            Flags = ScriptEntry.Flag.Local,
        };
        script.Properties.Add(
            new ScriptStringProperty
            {
                Name = "ModName",
                Flags = ScriptProperty.Flag.Edited,
                Data = options.ModName,
            }
        );
        quest.VirtualMachineAdapter.Scripts.Add(script);
        quest.NextAliasID = 1;
        var alias = new QuestAlias
        {
            ID = 0,
            Name = "PlayerAlias",
            Type = QuestAlias.TypeEnum.Reference,
        };
        alias.ForcedReference.SetTo(FormKey.Factory("000014:Skyrim.esm"));
        quest.Aliases.Add(alias);

        var property = new ScriptObjectProperty
        {
            Name = string.Empty,
            Flags = ScriptProperty.Flag.Edited,
            Alias = 0,
        };
        property.Object.SetTo(quest.FormKey);
        var attachment = new QuestFragmentAlias
        {
            Version = 5,
            ObjectFormat = 2,
            Property = property,
        };
        attachment.Scripts.Add(
            new ScriptEntry { Name = "SKI_PlayerLoadGameAlias", Flags = ScriptEntry.Flag.Local }
        );
        quest.VirtualMachineAdapter.Aliases.Add(attachment);
        return quest;
    }
}
