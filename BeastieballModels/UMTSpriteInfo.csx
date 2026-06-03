using System.IO;
using UndertaleModLib.Util;

EnsureDataLoaded();

string exportDir = PromptChooseDirectory();

string output = "{\n";
bool first = true;
bool last_null = false;

foreach (UndertaleSprite sprite in Data.Sprites) {
  if (!first) {
    if (!last_null) {
      output += "  },\n";
    }
  } else {
    first = false;
  }
  if (sprite.Textures.Count == 0 || sprite.Textures[0].Texture == null) {
    output += "";
    last_null = true;
    continue;
  }
  last_null = false;
  UndertaleTexturePageItem item = sprite.Textures[0].Texture;
  double pageWidth = item.TexturePage.TextureWidth;
  double pageHeight = item.TexturePage.TextureHeight;
  double sourceX = item.SourceX;
  double sourceY = item.SourceY;
  double sourceWidth = item.SourceWidth;
  double sourceHeight = item.SourceHeight;
  double sprWidth = sprite.Width;
  double sprHeight = sprite.Height;
  double targetX = item.TargetX;
  double targetY = item.TargetY;

  output += "  " + sprite.Name.ToString() + ": {\n";
  output += "    \"pageScaleX\": " + (pageWidth / sourceWidth).ToString() + ",\n";
  output += "    \"pageScaleY\": " + (pageHeight / sourceHeight).ToString() + ",\n";
  output += "    \"pageOffsetX\": " + (sourceX / pageWidth).ToString() + ",\n";
  output += "    \"pageOffsetY\": " + (sourceY / pageHeight).ToString() + ",\n";
  output += "    \"spriteScaleX\": " + (sourceWidth / sprWidth).ToString() + ",\n";
  output += "    \"spriteScaleY\": " + (sourceHeight / sprHeight).ToString() + ",\n";
  output += "    \"spriteOffsetX\": " + (targetX / sprWidth).ToString() + ",\n";
  output += "    \"spriteOffsetY\": " + (targetY / sprHeight).ToString() + "\n";
}
if (last_null) {
  output += "\n}\n";
} else {
  output += "  }\n}\n";
}
File.WriteAllText(exportDir + "/sprite_info.json", output);
