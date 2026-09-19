namespace BMK.Mutagen.Skyrim;

public sealed record McmQuestOptions
{
    public required string EditorId { get; init; }

    public required string DisplayName { get; init; }

    public required string ConfigScriptName { get; init; }

    public required string ModName { get; init; }
}
