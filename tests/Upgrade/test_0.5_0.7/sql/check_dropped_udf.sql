SELECT 'upgrade_madlib.compute_logregr(character varying, character varying, character varying, integer, character varying, double precision)'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_cg_result(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_cg_step_distance(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_igd_result(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_igd_step_distance(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_irls_result(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.internal_logregr_irls_step_distance(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr(character varying, character varying, character varying)'::regprocedure;
SELECT 'upgrade_madlib.logregr(character varying, character varying, character varying, integer)'::regprocedure;
SELECT 'upgrade_madlib.logregr(character varying, character varying, character varying, integer, character varying)'::regprocedure;
SELECT 'upgrade_madlib.logregr(character varying, character varying, character varying, integer, character varying, double precision)'::regprocedure;
SELECT 'upgrade_madlib.logregr_cg_step_final(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_cg_step_merge_states(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_cg_step_transition(double precision[], boolean, double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_igd_step_final(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_igd_step_merge_states(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_igd_step_transition(double precision[], boolean, double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_irls_step_final(double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_irls_step_merge_states(double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.logregr_irls_step_transition(double precision[], boolean, double precision[], double precision[])'::regprocedure;
SELECT 'upgrade_madlib.plda_cword_count(integer[], integer[], integer[], integer, integer, integer)'::regprocedure;
SELECT 'upgrade_madlib.plda_label_document(integer[], integer[], integer[], integer, integer, double precision, double precision)'::regprocedure;
SELECT 'upgrade_madlib.plda_label_test_documents(text, text, text, text, integer, double precision, double precision)'::regprocedure;
SELECT 'upgrade_madlib.plda_random_topics(integer, integer)'::regprocedure;
SELECT 'upgrade_madlib.plda_run(text, text, text, text, integer, integer, double precision, double precision)'::regprocedure;
SELECT 'upgrade_madlib.plda_sample_new_topics(integer[], integer[], integer[], integer[], integer[], integer, integer, double precision, double precision)'::regprocedure;
SELECT 'upgrade_madlib.plda_sum_int4array(integer[], integer[])'::regprocedure;
SELECT 'upgrade_madlib.plda_topic_word_prob(integer, integer, text, text)'::regprocedure;
SELECT 'upgrade_madlib.plda_train(integer, integer, double precision, double precision, text, text, text, text)'::regprocedure;
SELECT 'upgrade_madlib.plda_word_topic_distrn(integer[], integer, integer)'::regprocedure;
SELECT 'upgrade_madlib.plda_zero_array(integer)'::regprocedure;