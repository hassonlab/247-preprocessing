
PRJCT_ID := podcast
PRJCT_ID := tfs

CMD := echo
CMD := sbatch submit.sh
CMD := python

SID := 500
CONV_IDX := 798_30s_test

SID := 625
CONV_IDX := $(shell seq 0 53)
CONV_IDX := $(shell seq 0 0)

# SID := 676
# CONV_IDX := $(shell seq 0 77)

# SID := 717
# SID := 7170
# CONV_IDX := $(shell seq 1 24)

# SID := 798
# CONV_IDX := $(shell seq 0 14)
# CONV_IDX := 3


link-data:
ifeq ($(PRJCT_ID), podcast)
	$(eval DIR_KEY := podcast-data)
else
	$(eval DIR_KEY := conversations-car)
endif
	# create directory
	mkdir -p data/$(PRJCT_ID)
	# delete old symlinks
	find data/$(PRJCT_ID)/ -xtype l -delete
	# create symlinks from original data store
	ln -sf /projects/HASSON/247/data/$(DIR_KEY)/* data/$(PRJCT_ID)/

audio-prep:
	mkdir -p logs
	for conv in $(CONV_IDX); do \
		$(CMD) audio_prep.py \
			--sid $(SID) \
			--model large-v2 \
			--conv-idx $$conv; \
	done;