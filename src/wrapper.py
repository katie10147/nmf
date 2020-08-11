import os
os.chdir('/Users/katiepelton/Desktop/urban-aq/nmf/src')

exec(open("munge.py").read())
exec(open("nmf.py").read())
exec(open("bootstrap.py").read())
exec(open("figure.py").read())

#type into terminal $ python wrapper.py