File "/mount/src/rp-mobile-logger/app.py", line 25, in <module>
    creds = get_creds() or exchange_code_for_token()
                           ~~~~~~~~~~~~~~~~~~~~~~~^^
File "/mount/src/rp-mobile-logger/google_auth.py", line 34, in exchange_code_for_token
    params = params.to_dict() if params else st.experimental_get_query_params()
                                             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/deprecation_util.py", line 108, in wrapped_func
    result = func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 443, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/commands/experimental_query_params.py", line 61, in get_query_params
    ctx.mark_experimental_query_params_used()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner_utils/script_run_context.py", line 217, in mark_experimental_query_params_used
    self.ensure_single_query_api_used()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner_utils/script_run_context.py", line 209, in ensure_single_query_api_used
    raise StreamlitAPIException(
    ...<3 lines>...
    )

def sign_out():
    st.session_state.pop(CREDS_KEY, None)
