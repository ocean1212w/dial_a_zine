from lib.contents_reader import ContentsReader
import asyncio

CLEAR_SCREEN = "\u001b[2J"
NEW_LINE = "\r\n"

class ZineFunctions:
    def __init__(self, reader, writer, index_file_path):
        self.reader = reader
        self.writer = writer
        self.contents_reader = ContentsReader(index_file_path)
    
    async def run_index(self):
        for welcome_line in self.contents_reader.read_hello_file():
            self.writer.write(welcome_line)
        self.writer.write(NEW_LINE * 3)
        await self.writer.drain()
        # Read one byte (any key)
        await self.reader.read(1)
        running = True
        while (running):
            for index_line in self.contents_reader.read_index():
                self.writer.write(index_line)
            item_choice = await self.reader.read(1)
            item_choice_int = -1
            if item_choice.upper() == 'X':
                running = False
                continue
            item_choice_int = self.contents_reader.map_input_to_numerical_index(item_choice)
            if item_choice_int == -1:
                self.writer.write(f"{NEW_LINE}{NEW_LINE}Pick a story, or X to quit.{NEW_LINE}")
                continue
            self.writer.write(f"{NEW_LINE}{NEW_LINE}...you picked: %s" % (item_choice))
            self.writer.write(f"{NEW_LINE}{NEW_LINE}...press RETURN to start reading, and to continue after each page")
            await self.reader.read(1)
            self.writer.write(NEW_LINE + CLEAR_SCREEN)
            await asyncio.sleep(1)
            await self.run_story(item_choice_int)
        self.disconnect()
    
    async def run_story(self, story_number):
        page_number = 1

        story_lines = self.contents_reader.read_story(story_number, page_number)
        while len(story_lines) > 0:
            self.writer.write(CLEAR_SCREEN)
            for story_line in story_lines:
                self.writer.write(story_line)
            await self.writer.drain()
            char_read = await self.reader.readline()
            page_number += 1
            story_lines = self.contents_reader.read_story(story_number, page_number)
    
    def disconnect(self):
        self.writer.close()
