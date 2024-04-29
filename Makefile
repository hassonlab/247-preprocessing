
PRJCT_ID := podcast
PRJCT_ID := tfs

PIPELINE := whisperx

SID := 500
CONV_IDX := 798_30s_test

SID := 625
CONV_IDX := $(shell seq 1 54)

# SID := 676
# CONV_IDX := $(shell seq 1 78)
# CONV_IDX := $(shell seq 1 39)
# CONV_IDX := $(shell seq 40 78)

# SID := 7170
# CONV_IDX := $(shell seq 1 24)

# SID := 798
# CONV_IDX := $(shell seq 1 15)
# CONV_IDX := $(shell seq 1 7)
# CONV_IDX := $(shell seq 8 11)
# CONV_IDX := $(shell seq 12 14)


CMD := echo
CMD := sbatch submit.sh
CMD := python


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
			--model large-v3 \
			--conv-idx $$conv; \
	done;


audio-dia:
	mkdir -p logs
	$(CMD) audio_dia.py \
		--sid $(SID) \
		--conv-idx $(CONV_IDX); \

audio-eval:
	mkdir -p logs
	$(CMD) audio_eval.py \
		--sid $(SID);