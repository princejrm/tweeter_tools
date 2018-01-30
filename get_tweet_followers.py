#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

#purpose : to fetch twitter followers of a person
#usage : <executable> <twitter username>
#PLease fill in the access_token, access_token_secret, consumer_key,consumer_secret

from tweepy import OAuthHandler;
from tweepy import API
import json
from multiprocessing import Process,Queue,Event,Lock;
import time;
import atexit;
import random
import multiprocessing;
import sys

access_token = "fill in your access_token"
access_token_secret = "fill in your access_token_secret"
consumer_key = "fill in your consumer_key"
consumer_secret = "fill in your consumer_secret"
plist = [];
sleeptime = 6;

def get_names (api,tidlist,q,proceed,llock):
	iam_monitor = False;
	for tid in tidlist:
		try:
			jdata = api.get_user (tid);
			q.put(jdata);
			if iam_monitor:
				print multiprocessing.current_process().name, "Query successful openning the gate";
				proceed.set ();
				iam_monitor = False;
			time.sleep(random.randint(1,sleeptime));
		except:
			tidlist.append(tid);
			print multiprocessing.current_process().name, ": Query failed"
			if iam_monitor:
				time.sleep(random.randint((sleeptime * 5),(sleeptime * 10)));
				continue;
			else:
				if proceed.is_set ():
					llock.acquire ();
					if proceed.is_set ():
						proceed.clear ();
						iam_monitor = True;
						print multiprocessing.current_process().name, "will be monitor";
					llock.release ();
				if not iam_monitor:
					proceed.wait ();

def clear_process ():
	for p in plist:
		p.terminate ();
	print "Killed all spawned processes"

def get_followers (api,tid):
	print "Followers of ",tid
	print "==============================="
	q = Queue ();
	proceed = Event ();
	proceed.set ();
	llock = Lock ();
	flist = api.followers_ids(tid);
	lflist = len(flist);
	sflist = 0;
	atexit.register(clear_process);
	count = 0;
	while (sflist < lflist):
		ilist = flist[sflist:sflist+100];
		count += 1;
		p = Process (target = get_names,args=(api,ilist,q,proceed,llock),name="worker" + str(count));
		p.start ();
		plist.append(p);
		sflist += 100;

	print "Number of process : ",len(plist);

	try:
		i = 1;
		while True:
			qempty = False;
			if (q.empty ()):
				qempty = True;
			else:
				tuser = q.get ();
				print i, ": ",tuser.name;
				i += 1;
			if qempty:
				pempty = True;
				for p in plist:
					if p.is_alive ():
						pempty = False;
						break;
			if (qempty and pempty):
				break
	except Exception as e:
		print "Exception Happend", e;



if __name__ == "__main__":
	auth = OAuthHandler (consumer_key,consumer_secret);
	auth.set_access_token(access_token,access_token_secret);
	api = API(auth);
	get_followers(api,sys.argv[1]);



