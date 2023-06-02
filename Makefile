.PHONY: install_job
BATCH_JOB=org.dltj.crs2rss

all: install_job

install_job:
	cp $(BATCH_JOB).plist ~/Library/LaunchAgents
	launchctl unload ~/Library/LaunchAgents/$(BATCH_JOB).plist
	launchctl load ~/Library/LaunchAgents/$(BATCH_JOB).plist
	launchctl start $(BATCH_JOB)