#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	jsonc
Summary:	PHP C extension for JSON serialization
Summary(pl.UTF-8):	Rozszerzenie C PHP dla serializacji JSON
Name:		%{php_name}-pecl-%{modname}
Version:	1.3.6
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	65891642a4a0214bbe77e1b208cdd607
URL:		https://github.com/remicollet/pecl-json-c
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
Provides:	php(json) = %{version}
Obsoletes:	php-pecl-json < %{version}
%{?requires_php_extension}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Support for JSON (JavaScript Object Notation) serialization.

%description -l pl.UTF-8
php-json to bardzo szybkie rozszerzenie C PHP dla serializacji JSON
(JavaScript Object Notation).

%prep
%setup -qc
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=json.so \
	-m > modules.log
grep json modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

# no -devel yet
%{__rm} $RPM_BUILD_ROOT%{_includedir}/php/ext/json/php_json.h

# to simplify the rest, use jsonc.so as ext filename
mv $RPM_BUILD_ROOT%{php_extensiondir}/{json,%{modname}}.so

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md CREDITS INSTALL
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
