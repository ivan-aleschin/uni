{application, lab4_app,
 [{description, "Lab 4 OTP app"},
  {vsn, "1.0.0"},
  {modules, [lab4_app, lab4_sup, ring_srv, parent_children_srv]},
  {registered, [lab4_sup, ring_srv, parent_children_srv]},
  {applications, [kernel, stdlib]},
  {mod, {lab4_app, []}}]}.
