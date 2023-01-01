from collections import OrderedDict
from functools import partial
from time import sleep
from typing import Union
import regex
import os
from flatten_everything import flatten_everything, ProtectedList
import pandas as pd
from check_if_nan import is_nan as qq_s_isnan
from useful_functions_easier_life import NamedFunction
from a_selenium_iframes_crawler import Iframes


def _selenium_functions_(
    func, driver_, webelement, frame, iframes_, arguments, add_arguments
):

    if not isinstance(arguments, list):
        arguments = [arguments]
    try:
        iframes_.switch_to(frame)
        if add_arguments:
            executefunction = getattr(webelement, func)(*arguments)

        else:
            executefunction = getattr(webelement, func)()

        driver_.switch_to.default_content()
        if qq_s_isnan(executefunction):
            executefunction = True
        return executefunction
    except Exception as Fehler:
        print(Fehler)
        driver_.switch_to.default_content()
        return pd.NA


def _selenium_functions_no_args_partial(
    func, driver_, webelement, frame, iframes_, arguments="", add_arguments=False
):
    return NamedFunction(
        name="",
        execute_function=partial(
            _selenium_functions_,
            func,
            driver_,
            webelement,
            frame,
            iframes_,
            arguments=arguments,
            add_arguments=add_arguments,
        ),
        name_function=lambda: "()",
        str_prefix="",
        print_before_execution="",
        str_suffix="",
        ljust_prefix=0,
        rjust_prefix=0,
        ljust_suffix=0,
        rjust_suffix=0,
    )


def _selenium_functions_with_args_partial(
    func, driver_, webelement, frame, iframes_, add_arguments=True
):
    return NamedFunction(
        name="",
        execute_function=partial(
            _selenium_functions_,
            func,
            driver_,
            webelement,
            frame,
            iframes_,
            add_arguments=add_arguments,
        ),
        name_function=lambda: "()",
        str_prefix="",
        print_before_execution="",
        str_suffix="",
        ljust_prefix=0,
        rjust_prefix=0,
        ljust_suffix=0,
        rjust_suffix=0,
    )


def get_all_elements(driver_, By, WebDriverWait, expected_conditions, queryselector):
    getmet = """function getMethods(obj) {
      var result4 = [];
      if([false, 0, "", null, undefined, NaN].includes(obj)){
      return result4;
      }
      for (var id in obj) {
        if(![false, 0, "", null, undefined, NaN].includes(obj[id])){
        try {
        if (typeof(obj[id]) != "function") {
            result4.push(["AAAA",id,"AAAA",obj[id]]);
          }
          if (typeof(obj[id]) == "function") {
            result4.push(["FFFF",id,"FFFF",obj[id]]);
          }
        } catch (err) {
          result4.push(["FFFF","id","FFFF","obj[id]"]);
          continue;
        }}
      }
      return result4;
    }"""
    all_attributes = []
    driver_.switch_to.default_content()
    iframes = Iframes(
        driver=driver_,
        By=By,
        WebDriverWait=WebDriverWait,
        expected_conditions=expected_conditions,
    )
    for x in iframes.iframes.items():
        iframes.switch_to(x[0])

        attributes = driver_.execute_script(
            rf"""

                {getmet}

                var result = []; 
                var all = document.querySelectorAll(`{queryselector}`); 
                for (var i=0, max=all.length; i < max; i++) {{
            try {{
                result.push([all[i],getMethods(all[i]).join("ÇÇÇÇÇÇÇÇÇÇ")]);
                     }}           catch (err) {{
                    result.push([all[i],`ERROR`]);
              continue;

            }}
            }};
                return result;
            """
        )
        all_attributes.append((x[0], attributes))
    return iframes, all_attributes, list(iframes.iframes.keys())


def _normalize_result_dict(allelements, normalize_functions, normalize_attributes):
    ganzeliste = []
    for key in list(allelements.keys()):
        ganzeliste_tmp1 = []
        for key2 in allelements[key]:
            if key2 == "all_data":
                continue
            ganzeliste_tmp = []
            for key3 in allelements[key][key2]:
                if key2 == "webelements":
                    webelement = key3
                    ganzeliste_tmp.append({key: webelement})
                if key2 == "functions":
                    functions = key3
                    functiondict = OrderedDict(
                        {k: k if k in functions else pd.NA for k in normalize_functions}
                    )
                    ganzeliste_tmp.append(functiondict.copy())

                if key2 == "attributes":
                    attrib = key3
                    attribdict_list = []

                    for aa in attrib:
                        attribdict = OrderedDict()

                        for aa_ in aa:
                            newvalue = aa_[1]
                            if (aa_[0]) not in normalize_attributes:
                                attribdict[(aa_[0])] = newvalue

                            if str(newvalue).isdigit():
                                newvalue = int(newvalue)
                            elif str(newvalue).replace(".", "").isdigit() and len(
                                str(newvalue).replace(".", "")
                            ) + 1 == len(str(newvalue)):
                                newvalue = float(newvalue)
                            elif str(newvalue) == "true":
                                newvalue = True
                            elif str(newvalue) == "false":
                                newvalue = False
                            attribdict[(aa_[0])] = newvalue
                        for all_attributes in normalize_attributes:
                            if all_attributes not in attribdict:
                                attribdict[all_attributes] = pd.NA
                        attribdict_list.append(attribdict.copy())
                    ganzeliste_tmp.append([attribdict_list.copy()])
            ganzeliste_tmp1.append(ganzeliste_tmp.copy())
        ganzeliste.append(ganzeliste_tmp1.copy())
    return ganzeliste


def _search_result_to_dict(all_attributes, iframes, iframenames):
    allelements = {}
    regex_compiled_functions = regex.compile("^FFFF,([^,]+),")
    normalize_attributes = []
    normalize_functions = []
    for number in range(len(iframes.iframes)):
        all_data = [
            [x for x in (all_attributes[number][1][z][1]).split("ÇÇÇÇÇÇÇÇÇÇ")]
            for z in range(len(all_attributes[number][1]))
        ]
        webelements = [
            [
                (all_attributes[number][1][z][0])
                for z in range(len(all_attributes[number][1]))
            ]
        ]
        attributes = [
            [a if a.startswith("AAAA") else None for a in all_data[b]]
            for b in range(len(all_data))
        ]
        attributes = [[y for y in x if y is not None] for x in attributes]
        attributes = [
            [y.split("AAAA,", maxsplit=2)[1:][::1] for y in x] for x in attributes
        ]
        attributes_ = [
            [
                list([[z.strip().strip(""""\',""") for z in y][0] for y in x])
                for x in attributes
            ]
        ]
        attributes = [
            [
                ProtectedList([[z.strip().strip(""""\',""") for z in y] for y in x])
                for x in attributes
            ]
        ]

        functions = [
            [a if a.startswith("FFFF") else None for a in all_data[b]]
            for b in range(len(all_data))
        ]
        functions = [
            list(
                flatten_everything(
                    [regex_compiled_functions.findall(y) for y in x if y is not None]
                )
            )
            for x in functions
        ]
        normalize_attributes.extend(attributes_.copy())
        normalize_functions.extend(functions.copy())

        allelements[iframenames[number]] = {
            "all_data": all_data.copy(),
            "webelements": webelements.copy(),
            "attributes": attributes.copy(),
            "functions": functions.copy(),
        }
    normalize_functions = list(
        dict.fromkeys(list(flatten_everything(normalize_functions)))
    )
    normalize_attributes = list(
        dict.fromkeys(list(flatten_everything(normalize_attributes)))
    )
    return allelements, normalize_functions, normalize_attributes


def _result_dict_to_dataframe(ganzeliste):
    dfs = []
    for fra in ganzeliste:
        dfs.append([pd.DataFrame(_) for _ in fra])
    adjustedframesall = []
    for ini, dframestemp in enumerate(dfs):
        adjustedframes = []

        for ini2, each_frame in enumerate(dframestemp):
            if ini2 == 0:
                each_frameadjusted = each_frame.explode(each_frame.columns[0]).copy()
                each_frameadjusted[
                    "frame"
                ] = each_frameadjusted.columns.to_list() * len(each_frameadjusted)
                each_frameadjusted["elements_in_frame"] = len(each_frameadjusted)

                adjustedframes.append(each_frameadjusted.reset_index(drop=True).copy())
            elif ini2 == 1:
                each_frame_ = (
                    each_frame.explode(0)[0].apply(lambda x: pd.Series(x)).copy()
                )
                each_frame_.columns = [f"aa_{x}" for x in each_frame_.columns.to_list()]
                adjustedframes.append(each_frame_.reset_index(drop=True).copy())

            else:
                each_frame_ = each_frame.copy()
                each_frame_.columns = [f"js_{x}" for x in each_frame_.columns.to_list()]

                adjustedframes.append(each_frame_.reset_index(drop=True).copy())
        concatelements = pd.concat(adjustedframes.copy(), axis=1)
        concatelements.columns = ["element"] + concatelements.columns.to_list()[1:]
        adjustedframesall.append(concatelements.copy())
    df = (
        pd.concat(adjustedframesall.copy(), ignore_index=True)
        .dropna(subset=["element"])
        .copy()
    )
    columnstodrop = []
    for _ in [
        x for x in df.columns.to_list() if x.startswith("aa_") or x.startswith("js_")
    ]:
        try:
            if (df[_].nunique()) == 1 and _.startswith("aa_"):
                columnstodrop.append(_)
            if (df[_].nunique()) == 1 and _.startswith("js_"):
                if qq_s_isnan(df[_].iloc[0]):
                    columnstodrop.append(_)
        except Exception as Fehler:
            print(Fehler)

    if "aa_0" in df.columns:
        columnstodrop.append("aa_0")

    df = df.drop(columns=columnstodrop).copy()
    return df


def execute_jsript_function(
    driver_,
    webelement,
    frame,
    iframes_,
    function_name: str,
    arguments: Union[list, str] = "",
):
    if isinstance(arguments, list):
        ", ".join(arguments).strip(" ,")
    try:
        iframes_.switch_to(frame)
        jscriptresult = driver_.execute_script(
            f"return arguments[0].{function_name}({arguments});", webelement
        )
        driver_.switch_to.default_content()
        return jscriptresult
    except Exception as Fehler:
        driver_.switch_to.default_content()
        return pd.NA


def create_function(driver_, webelement, frame, function_name, iframes_):

    return NamedFunction(
        name="",
        execute_function=partial(
            execute_jsript_function, driver_, webelement, frame, iframes_, function_name
        ),
        name_function=lambda: "()",
        str_prefix="",
        print_before_execution="",
        str_suffix="",
        ljust_prefix=0,
        rjust_prefix=0,
        ljust_suffix=0,
        rjust_suffix=0,
    )


def wheel_element(
    driver_,
    webelement,
    iframes_,
    frame,
    deltaY=120,
    offsetX=0,
    offsetY=0,
    script_timeout=1,
):
    # https://stackoverflow.com/questions/55371752/how-do-i-use-multi-line-scripts-in-selenium-to-execute-a-script

    oldvalue = driver_.__dict__["caps"]["timeouts"]["script"]
    driver_.set_script_timeout(script_timeout)

    try:
        iframes_.switch_to(frame)
        jscriptresult = webelement._parent.execute_script(
            """
        var element = arguments[0];
        var deltaY = arguments[1];
        var box = element.getBoundingClientRect();
        var clientX = box.left + (arguments[2] || box.width / 2);
        var clientY = box.top + (arguments[3] || box.height / 2);
        var target = element.ownerDocument.elementFromPoint(clientX, clientY);

        for (var e = target; e; e = e.parentElement) {
          if (e === element) {
            target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
            target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
            target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
            return;
          }
        }    
        return "Element is not interactable";
        """,
            webelement,
            deltaY,
            offsetX,
            offsetY,
        )
        driver_.switch_to.default_content()
        driver_.set_script_timeout(oldvalue)
        if jscriptresult is None:
            return True
        return False
    except Exception as Fehler:
        driver_.switch_to.default_content()
        return pd.NA


def switch_to_window(driver, cwh):
    return NamedFunction(
        name="",
        execute_function=partial(driver.switch_to.window, cwh),
        name_function=lambda: "()",
        str_prefix=cwh,
        print_before_execution="",
        str_suffix="",
        ljust_prefix=0,
        rjust_prefix=0,
        ljust_suffix=0,
        rjust_suffix=0,
    )


def change_html_code_of_element(
    driver, element, iframes_, frame, htmlcode, script_timeout=2
):
    iframes_.switch_to(frame)
    oldvalue = driver.__dict__["caps"]["timeouts"]["script"]
    driver.set_script_timeout(script_timeout)
    driver.execute_script(f"arguments[0].innerHTML = `{htmlcode}`;", element)
    driver.switch_to.default_content()
    driver.set_script_timeout(oldvalue)


def _switch_to_frame(frame, iframes_):
    iframes_.switch_to(frame)


def _location_once_scrolled_into_view(driver_, webelement, frame, iframes_):
    try:
        iframes_.switch_to(frame)

        webelement.location_once_scrolled_into_view
        driver_.switch_to.default_content()
        return True

    except Exception as Fehler:
        print(Fehler)
        return pd.NA


def location_once_scrolled_into_view_partial(driver_, webelement, frame, iframes_):
    return NamedFunction(
        name="",
        execute_function=partial(
            _location_once_scrolled_into_view, driver_, webelement, frame, iframes_
        ),
        name_function=lambda: "()",
        str_prefix="",
        print_before_execution="",
        str_suffix="",
        ljust_prefix=0,
        rjust_prefix=0,
        ljust_suffix=0,
        rjust_suffix=0,
    )


def _functions_to_dataframe(df, driver_, iframes):
    for col in df.columns:
        if str(col).startswith("js_"):
            df[col] = df.apply(
                lambda x: create_function(driver_, x.element, x.frame, x[col], iframes),
                axis=1,
            )

    df["js_wheel"] = df.apply(
        lambda x: NamedFunction(
            name="",
            execute_function=partial(
                wheel_element, driver_, x.element, iframes, x.frame
            ),
            name_function=lambda: "()",
            str_prefix="",
            print_before_execution="",
            str_suffix="",
            ljust_prefix=0,
            rjust_prefix=0,
            ljust_suffix=0,
            rjust_suffix=0,
        ),
        axis=1,
    )

    df["js_change_html_value"] = df.apply(
        lambda x: NamedFunction(
            name="",
            execute_function=partial(
                change_html_code_of_element, driver_, x.element, iframes, x.frame
            ),
            name_function=lambda: "()",
            str_prefix="",
            print_before_execution="",
            str_suffix="",
            ljust_prefix=0,
            rjust_prefix=0,
            ljust_suffix=0,
            rjust_suffix=0,
        ),
        axis=1,
    )

    df["se_send_keys"] = df.apply(
        lambda x: _selenium_functions_with_args_partial(
            "send_keys", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )

    df["se_find_elements"] = df.apply(
        lambda x: _selenium_functions_with_args_partial(
            "find_elements", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )
    df["se_find_element"] = df.apply(
        lambda x: _selenium_functions_with_args_partial(
            "find_element", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )
    df["se_is_displayed"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "is_displayed", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )
    df["se_is_enabled"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "is_enabled", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )
    df["se_is_selected"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "is_selected", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )
    df["se_clear"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "clear", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )

    df["se_click"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "click", driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )

    df["se_switch_to_frame"] = df.apply(
        lambda x: _switch_to_frame(x.frame, iframes),
        axis=1,
    )
    df["se_location_once_scrolled_into_view"] = df.apply(
        lambda x: location_once_scrolled_into_view_partial(
            driver_, x.element, x.frame, iframes
        ),
        axis=1,
    )

    folder = os.getcwd()
    folder = os.path.join(folder, "seleniumpictures")
    if not os.path.exists(folder):
        os.makedirs(folder)
    df["se_get_screenshot_as_file"] = df.index.astype(str) + ".png"
    df["se_get_screenshot_as_file"] = df["se_get_screenshot_as_file"].apply(
        lambda x: os.path.join(folder, x)
    )
    df["se_screenshot"] = df.apply(
        lambda x: _selenium_functions_no_args_partial(
            "screenshot",
            driver_,
            x.element,
            x.frame,
            iframes,
            x.se_get_screenshot_as_file,
            True,
        ),
        axis=1,
    )
    return df


def get_df(
    driver_,
    By,
    WebDriverWait,
    expected_conditions,
    queryselector="*",
    repeat_until_element_in_columns=None,
    max_repeats=1,
    with_methods=True,
):
    howmanyloops = max_repeats if repeat_until_element_in_columns is not None else 1
    df = pd.DataFrame()
    regexstart = regex.compile(r"^(?:(?:aa)|(?:bb)|(?:ff))_")
    for _ in range(howmanyloops):
        iframes, all_attributes, iframenames = get_all_elements(
            driver_=driver_,
            By=By,
            WebDriverWait=WebDriverWait,
            expected_conditions=expected_conditions,
            queryselector=queryselector,
        )
        allelements, normalize_functions, normalize_attributes = _search_result_to_dict(
            all_attributes, iframes, iframenames
        )
        ganzeliste = _normalize_result_dict(
            allelements, normalize_functions, normalize_attributes
        )
        df = _result_dict_to_dataframe(ganzeliste)
        if with_methods:
            df = _functions_to_dataframe(df, driver_, iframes)
        if repeat_until_element_in_columns is not None:
            allcollis = [
                x
                for x in df.columns
                if regexstart.sub("", str(x)).strip()
                == regexstart.sub("", str(repeat_until_element_in_columns)).strip()
            ]
            if any(allcollis):
                break
            else:
                sleep(1)

    cwh = driver_.current_window_handle
    windowswitchlist = [switch_to_window(driver_, cwh) for x in range(len(df))]

    df["aa_window_handle"] = cwh
    df["aa_window_switch"] = windowswitchlist

    return df
