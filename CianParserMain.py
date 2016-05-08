# -*- coding: utf-8 -*-
import LoggerInit
import config
from Parsers.CianParserProcess import main

if __name__ == "__main__":
    LoggerInit.init_logging(config.log_parser_file)
    main()
