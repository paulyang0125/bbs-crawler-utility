##################################################################################
#                                                                                #
#  Copyright (c) 2014 Yao Nien, Yang, paulyang0125@gmail.com                     #  
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not   #
#  use this file except in compliance with the License. You may obtain a copy    #
#  of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless required #
#  by applicable law or agreed to in writing, software distributed under the     #
#  License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS  #
#  OF ANY KIND, either express or implied. See the License for the specific      #
#  language governing permissions and limitations under the License.             # 
#                                                                                #
##################################################################################

import bs4
import urllib2
import re
import time
import logging
import json
from optparse import OptionParser
from optparse import Option, OptionValueError
import os, sys

MYCOMPUTERPATH = "C:/bbs_crawler/BBS"
ROOTPATH = "C:/bbs_crawler"
FETCH_PATH = MYCOMPUTERPATH + '/fetched'
LOGNAME = 'log'
VERSION = '0.2'

class BBSCrawler(object):
    '''
    @author: Paul Yang
    @note: This prog is to fetch the ptt's content based on the board name like car  and the fetched files will be stored under the directory "./fetched/BOARDNAME/"
    @since: 2014/8/2, v0.2
    '''

    def __init__(self, board_name = 'car', myPageNum = 10, toNum = 0,debugFlag = False, forAll = False):
        '''
        Constructor
        '''
        self.useHeader = False
        ## debug flag to enable debug - not finished yet.
        self.debugFlag = debugFlag
        self.board_name = board_name
        
        ## put the cookie header for the board like Gossiping to pass around the limit of 18 age 
        if self.board_name == 'Gossiping':
            self.initHeader()
            self.useHeader = True
        
        self.myPageNum = myPageNum
        
        ## if forAll is on, iterate the total number of pages for the board by getAllPagesInTheBoard()    
        self.forAll = forAll
        self.toNum = toNum
        self.path = os.path.join(FETCH_PATH, self.board_name)
        self.ESPECIAL_URL = 'http://www.ptt.cc/bbs/' + self.board_name + '/index' + '.html'
        self.post_url = lambda id: 'http://www.ptt.cc/bbs/' + self.board_name + '/' + id + '.html'
        self.page_url = lambda n: 'http://www.ptt.cc/bbs/' + self.board_name + '/index' + str(n) + '.html'
        self.initLogging()
        self.statisticDic = dict()
        self.num_pushes = dict()
        self.metadic = dict()
        os.chdir(self.path)
        sys.stderr.write('Crawling "%s" ...\n' % self.board_name)
        self.logger.info('Crawling "%s" ...\n' % self.board_name)
        
        
    ## for over 18 content, need to put the header 
    def initHeader(self): 
        self.headers = dict()
        self.headers['Cookie'] = str('over18=1; __utma=156441338.1052450315.1398943535.1398943535.1398943535.1; __utmb=156441338.2.10.1398943535; __utmc=156441338; __utmz=156441338.1398943535.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)' )
        
        
    def initLogging(self):
        '''
        initializing logging function and put to /bbsCrawler.log
        '''
        print "initializing the logging ......."
        myLogPath = os.path.join(self.path, LOGNAME)
        try:
            os.makedirs(myLogPath)
        except: 
            sys.stderr.write('Warning: "%s" already existed\n' % myLogPath)
        LOGPATH = myLogPath + '/bbsCrawler.log'
        #logger.warn('Warning: "%s" already existed\n' % myLogPath)
        self.logger = logging.getLogger('bbs crawler')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr = logging.FileHandler(LOGPATH)
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        #logger.setLevel(logging.DEBUG)
        self.logger.info('bbs crawler started')
    
    def remove_html_tags(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
    def closeLogging(self):
        self.logger.info('closing logging')
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
    
    def getAllPagesInTheBoard(self):
        self.logger.info('getting all pages number from "%s" ...\n' % self.board_name)
        try:
            if (self.useHeader):
                request = urllib2.Request(self.ESPECIAL_URL, headers=self.headers)
                indexPage = bs4.BeautifulSoup(urllib2.urlopen(request).read())
            else:
                indexPage = bs4.BeautifulSoup(urllib2.urlopen(self.ESPECIAL_URL).read())
            ## filter '/bbs/car/index1275.html' to number only "1275"
            self.allPageNums = int(re.sub(r'[^0-9]+', '', indexPage.find_all("a", class_="btn wide")[1].get('href')))
            sys.stderr.write('Total number of pages: %d\n' % self.allPageNums)
            self.logger.error('Total number of pages: %d\n' % self.allPageNums)
        except:
            sys.stderr.write('can not get the number of pages')
            self.logger.error('cannot get the number of pages \n')
    
    def getContent(self):
        start_time = time.time()
        
        if (not self.forAll): 
            ##use self.myPageNum for designate page 
            pagesToRun = self.myPageNum
        else:
            ##use all number got from getAllPagesInTheBoard()
            pagesToRun = self.allPageNums
        
        if (self.toNum != 0 and not self.forAll): ## to suport 2 arguments start 3 -> 100
            startIndex = pagesToRun
            endIndex = self.toNum
        else:
            startIndex = 1
            endIndex = pagesToRun
        

        ## add the index to record the total number that has processed, the number of failure and the number of success
        self.statisticDic['indexFailure'] = 0
        self.statisticDic['totalPostNum'] = 0
        self.statisticDic['fetchFailureNum'] = 0

        ## iterate through index page like "www.ptt.cc/bbs/car/index.html" to get each POST ID  
        #for indexP in xrange(1, pagesToRun + 1):
        for indexP in xrange(startIndex, endIndex):
            sys.stderr.write('start from index %s ...\n' % indexP)
            self.logger.debug('start from index %s ...\n' % indexP)
            try:
                if (self.useHeader): ## if the page require header 
                    request = urllib2.Request(self.page_url(indexP), headers=self.headers)
                    page = bs4.BeautifulSoup(urllib2.urlopen(request).read())
                else:
                    page = bs4.BeautifulSoup(urllib2.urlopen(self.page_url(indexP)).read())
            except:
                sys.stderr.write('Error occured while fetching %s\n' % self.page_url(indexP))
                self.logger.error('Error occured while fetching %s\n' % self.page_url(indexP))
                ## how many index has failed 
                self.statisticDic['indexFailure'] += 1
                continue
            
            ## iterate through posts on this page
            for link in page.find_all(class_='r-ent'):
                
                try: 
                    ## For instance: "M.1368632629.A.AF7"
                    post_id = link.a.get('href').split('/')[-1][:-5]
                    ## Record the number of pushes from <div class="nrec">, which is an integer from -100 to 100
                    if (link.span):
                        self.num_pushes[post_id] = int(link.span.contents[0])
                    ## if can't find push, set 0 push 
                    else:
                        self.num_pushes[post_id] = 0
                    
                except:
                    sys.stderr.write('Error occured while fetching %s\n' % post_id)
                    self.logger.error('Error occured while fetching %s\n' % post_id)
                    continue
                
                ## Fetch the post content via post id, ex. http://www.ptt.cc/bbs/car/M.1400136465.A.DD5.html     
                self.statisticDic['totalPostNum'] += 1
                try:
                                            
                    sys.stderr.write('Fetching %s ...\n' % post_id)
                    self.logger.info('Fetching %s ...\n' % post_id)
                    if (self.useHeader): ## if the page require header 
                        request = urllib2.Request(self.post_url(post_id), headers=self.headers)
                        post = bs4.BeautifulSoup(urllib2.urlopen(request).read())
                    else:
                        post = bs4.BeautifulSoup(urllib2.urlopen(self.post_url(post_id)).read())
                except:
                    sys.stderr.write('Error occured while fetching %s\n' % self.post_url(post_id))
                    self.logger.error('Error occured while fetching %s\n' % self.post_url(post_id))
                    ##self.fetchFailureNum += 1
                    self.statisticDic['fetchFailureNum'] += 1
                    continue
    
                ## writing the content file named post ID 
                with open(post_id, 'w') as contentFile_fp, open(post_id + ".html", 'w') as contentHTML_fp:
                    contentFile_fp.write('Title:' + post.title.string.encode('utf-8') + '\n' + '\n' ) ## write title in a first line
                    contentFile_fp.write(self.remove_html_tags(str(post.find(id='main-container'))))
                    contentHTML_fp.write(post.prettify().encode('utf-8'))
                    contentHTML_fp.close()
                    contentFile_fp.close()
                
                os.chdir(self.path)
                ## delay for a little while in fear of getting blocked
                time.sleep(0.1)

        
        ## dump the number of pushes mapping to the file 'num_pushes_json'
        
        with open('num_pushes_json', 'w') as numPushesFp, open('metadata_dic_json', 'w') as metadataDicFp:
            self.logger.info('Saving the metadata dic and push mapping into JSON')
            #numPushesFp = open('num_pushes_json', 'w')
            #metadataDicFp = open('metadata_dic_json', 'w')
            json.dump(self.num_pushes, numPushesFp)
            json.dump(self.metadic, metadataDicFp)
            numPushesFp.close()
            metadataDicFp.close()
            
        ## do the final logging and printing all numbers     
        self.logger.info('Ending crawling "%s" ... !! \n' % self.board_name)
        self.logger.info('\n')
        self.logger.info('Statistic: \n')
        self.logger.info('indexFailure number: "%s" \n' % self.statisticDic['indexFailure'])
        self.logger.info('totalPost number: "%s" \n' % self.statisticDic['totalPostNum'])
        self.logger.info('fetchFailure number: "%s"  \n' % self.statisticDic['fetchFailureNum'])
        self.logger.info('\n')
        os.chdir(FETCH_PATH)
        print "the dir is: %s" %os.listdir(os.getcwd())
        self.closeLogging()
        os.rename(self.board_name,self.board_name + "_" + str(self.myPageNum) + "_" + str(self.toNum))
        elapsed_time = time.time() - start_time
        print "the dir is: %s" %os.listdir(os.getcwd())
        print "the total post num: %s" % self.statisticDic['totalPostNum']
        print "elapsed time: %s" % elapsed_time




def process(options, args):
    #print options.commands[0]
    #print args[0]
    if options.commands[0] == 'fetch_index':
        print ("start fetch the index %s"  % args[0])
        board_name = args[0]
        bbsCrawler = BBSCrawler(board_name)
        bbsCrawler.getAllPagesInTheBoard()
        print "fetching index number done!"
    
    elif options.commands[0] == 'fetch_page':
        print ("start fetch the index %s"  % args[0])
        board_name = args[0]
        myPageNum = int(args[1])
        bbsCrawler = BBSCrawler(board_name,myPageNum)
        bbsCrawler.getContent()
        print "fetching page done!"
        

class MultipleOption(Option):
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).append(value)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)   


###
### Usually run the program as: 
###
### ./bbs_crawler_public.py -c fetch_index car  
### ./bbs_crawler_public.py -c fetch_page car 6 
### Under DOS, python bbs_crawler_public.py -c fetch_page car 6
###  the fetched pages are in C:\bbs_crawler\BBS\fetched\"boardname" + indexNum



def main():
    
    PROG = os.path.basename(os.path.splitext(__file__)[0])
    long_commands = ('commands')
    short_commands = {'cmds':'commands'}
    description = """BBS crawler, use """
    parser = OptionParser(option_class=MultipleOption,
                         usage='usage: %prog [OPTIONS] ptt board_name index_number',
                         version='%s %s' % (PROG, VERSION),
                         description=description)
    
    parser.add_option('-c', '--commands', 
                      action="extend", type="string",
                      dest='commands', 
                      metavar='COMMANDS', 
                      help='select the commands like fetch_index with board_name or fetch_page with index_number you want the crawler to fetch  ')
    
    
    
    
    if len(sys.argv) == 1:
        parser.parse_args(['--help'])
    else:
        options, args = parser.parse_args()
        print "arguments:", args
        print "options:", options
        process(options, args)
        


if __name__ == '__main__':
    main()





#### invoke class directly for debug or integration 

#myPageNum = 2
#board_name = 'car'
#bbsCrawler = BBSCrawler(myPageNum,board_name)
#bbsCrawler.getAllPagesInTheBoard()
#bbsCrawler.getContent()

        