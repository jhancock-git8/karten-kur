# Importing AlgoApp Decks on iPhone

This guide explains how to transfer split deck XML files to an iPhone and import them back into AlgoApp.

## 1. Prepare the exported deck files

1. Use the script output in `output/` (for example `Jon-part1.xml`, `Jon-part2.xml`, etc.).
2. Verify each file is a valid AlgoApp deck export.
3. If needed, compress the files into a ZIP archive to simplify transfer.

## 2. Transfer files to iPhone

### Option A: AirDrop

1. On your iPhone, open the Files app and make sure AirDrop is enabled in Control Center.
2. On your Mac or Windows PC with AirDrop support, share the XML or ZIP file to the iPhone.
3. Accept the transfer on the iPhone.
4. In the iPhone Files app, choose a destination folder such as `On My iPhone` > `Downloads`.

### Option B: iCloud Drive

1. Put the XML or ZIP files into a folder inside iCloud Drive on your computer.
2. Wait for iCloud sync to complete.
3. Open the Files app on iPhone and navigate to the same iCloud Drive folder.

### Option C: Dropbox / OneDrive / Google Drive

1. Upload files to a cloud storage account from your computer.
2. Open the corresponding app on the iPhone.
3. Download the files or open them in the Files app.

### Option D: Email or messaging service

1. Attach the XML or ZIP file to an email and send it to yourself.
2. Open the email on the iPhone and tap the attachment.
3. Choose `Save to Files` and place it in a convenient folder.

### Option E: USB transfer via Finder (macOS) or iTunes (Windows)

1. Connect the iPhone to the computer with a USB cable.
2. On macOS, open Finder and select your device.
   - Go to the `Files` tab.
   - Drag the XML files into a supported app folder or the Files app if available.
3. On Windows, open iTunes and use File Sharing if the app supports it.

## 3. Import decks into AlgoApp

1. Open AlgoApp on the iPhone.
2. Look for an import button or menu in the deck management area.
3. If AlgoApp supports opening files from the Files app, choose the XML file from the folder where you saved it.
4. If the file is zipped, unzip it first within Files or a compatible app, then import the `.xml` file.
5. Follow the app prompts to confirm the import.

## 4. If AlgoApp does not see the file

- Make sure the XML file extension is `.xml`.
- Confirm the file was saved to `On My iPhone` or an accessible location in Files.
- If import still fails, try opening the file from Files and using `Share` > `Copy to AlgoApp` or `Open in AlgoApp`.
- Some apps require a specific folder or document provider; check AlgoApp settings for import sources.

## 5. Verify imported deck

1. Open the imported deck in AlgoApp.
2. Check the card count and a few sample cards.
3. Ensure the front/back text renders correctly and that any formatting is preserved.

## 6. Best practices

- Transfer one split file at a time if AlgoApp is sensitive to large decks.
- Keep a backup copy of the original XML files in iCloud Drive or on your computer.
- If using ZIP files, unzip them on the iPhone before importing.
- Prefer clean XML exports over multiple nested archives to reduce importer errors.
