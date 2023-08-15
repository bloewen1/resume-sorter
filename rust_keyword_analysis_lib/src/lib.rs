// src/lib.rs

use std::collections::HashMap;
use regex::Regex;

#[no_mangle]
pub extern "C" fn analyze_keywords(contents: *const u8, contents_len: usize) -> *const u8 {
    let contents_slice = unsafe { std::slice::from_raw_parts(contents, contents_len) };
    let contents_str = std::str::from_utf8(contents_slice).unwrap();

    let re = Regex::new(r"([a-zA-Z]+)").unwrap();
    let mut keywords = HashMap::new();

    for cap in re.captures_iter(contents_str) {
        let keyword = cap[0].to_string();
        let count = keywords.entry(keyword).or_insert(0);
        *count += 1;
    }

    let analysis_result = keywords.iter()
        .map(|(keyword, count)| format!("{}: {} occurrences", keyword, count))
        .collect::<Vec<_>>()
        .join("\n");

    let result_bytes = analysis_result.as_bytes();
    result_bytes.as_ptr()
}

