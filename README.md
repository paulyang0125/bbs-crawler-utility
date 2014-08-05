<h1> bbs_crawler_utility </h1>
===================

This prog is to fetch the ptt's content based on the board name like car 




<h2> Example Usage:</h2>

  bbs_crawler_public.exe [OPTIONS] ptt's board_name index_number
  
  You can use bbs_crawler to figure out how many index page the PTT board is by "fetch_index" option and fetch the 
  post page against each index by "fetch_page" plus the designated end of index to iterate from index 1 to yours 
  designation.




example: 
  if you install python already, 
  run bbs_crawler_public.py with fetch_index plus ptt's board name like the following  
  $python bbs_crawler_public.py -c fetch_index car
  
  or
  
  run bbs_crawler_public.py with fetch_page plus the designated end of index number like the following - iterate from 
  index 1 to index 6
  $python bbs_crawler_public.py -c fetch_page car 6 

  if you do not install python and use Windows OS, use bbs_crawler_public.exe instead of bbs_crawler_public.py to run the examples above 
  
  For more info, there's the blog in Chinese explain what and how it works. 
  抓取批踢踢 (Ptt) post文的crawler實作 - http://paulyang0125.blogspot.com/2014/08/ptt-postcrawler.html
  
  
