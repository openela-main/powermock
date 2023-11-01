Name:           powermock
Version:        1.6.5
Release:        9%{?dist}
Summary:        A Java mocking framework

# Note: api-mockito subpackage is ASL 2.0 and MIT, the rest is ASL 2.0
License:        ASL 2.0
URL:            https://github.com/jayway/powermock
Source0:        https://github.com/jayway/%{name}/archive/%{name}-%{version}.tar.gz

Patch1:         0001-Fix-junit3-compat.patch
# powermock contains forked version of mockito
# this is the same patch as in mockito to fix incompatibility with our cglib
Patch2:         0002-Setting-naming-policy.patch

BuildArch:      noarch

BuildRequires:  maven-local
BuildRequires:  mvn(cglib:cglib-nodep)
BuildRequires:  mvn(commons-logging:commons-logging)
BuildRequires:  mvn(javax.servlet:servlet-api)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.assertj:assertj-core)
BuildRequires:  mvn(org.easymock:easymock)
BuildRequires:  mvn(org.hamcrest:hamcrest-core)
BuildRequires:  mvn(org.javassist:javassist)
BuildRequires:  mvn(org.mockito:mockito-core)
BuildRequires:  mvn(org.objenesis:objenesis)
BuildRequires:  mvn(org.sonatype.oss:oss-parent:pom:)
BuildRequires:  mvn(org.testng:testng)


%global desc \
PowerMock is a framework that extend other mock libraries\
such as EasyMock with more powerful capabilities. PowerMock uses a\
custom classloader and bytecode manipulation to enable mocking of\
static methods, constructors, final classes and methods, private\
methods, removal of static initializers and more.

%description
%{desc}

%package common
Summary:        Common files for PowerMock

%description common
%{desc}

This package contains common files for all PowerMock modules.

%package reflect
Summary:        Reflection module of PowerMock
Requires:       %{name}-common = %{version}-%{release}

%description reflect
%{desc}

This package contains the reflection module of PowerMock.

%package core
Summary:        Core module of PowerMock
Requires:       %{name}-common = %{version}-%{release}

%description core
%{desc}

This package contains the core module of PowerMock.

%package junit4
Summary:        JUnit4 common module of PowerMock
Requires:       %{name}-common = %{version}-%{release}

%description junit4
%{desc}

This package contains the JUnit4 module of PowerMock.

%package api-support
Summary:        PowerMock API support module
Requires:       %{name}-common = %{version}-%{release}

%description api-support
%{desc}

This package contains support code for the PowerMock API extensions.

%package api-mockito
Summary:        PowerMock Mockito API module
# Bundles forked mockito, which is under MIT
License:        ASL 2.0 and MIT
Provides:       bundled(mockito) = 2.0
Requires:       %{name}-common = %{version}-%{release}

%description api-mockito
%{desc}

This package contains the PowerMock Mockito API extension.

%package api-easymock
Summary:        PowerMock EasyMock API module
Requires:       %{name}-common = %{version}-%{release}

%description api-easymock
%{desc}

This package contains the PowerMock EasyMock API extension.

%package testng
Summary:        PowerMock module for TestNG.
Requires:       %{name}-common = %{version}-%{release}

%description testng
%{desc}

This package contains the PowerMock TestNG extension.


%package javadoc
Summary:        JavaDocs for %{name}

%description javadoc
%{desc}

This package contains the API documentation for %{name}.

%prep
%setup -q -n %{name}-%{name}-%{version}

%patch1 -p1
%patch2 -p1

# bundled sources of various libraries
rm -r modules/module-impl/agent
# there is forked mockito, which contains bundled cglib and asm
rm -r api/mockito2/src/main/java/org/powermock/api/mockito/repackaged/{cglib,asm}

find -name '*.java' | xargs sed -i 's/org\.mockito\.cglib/net.sf.cglib/g;
                                    s/org\.powermock\.api\.mockito\.repackaged\.cglib/net.cf.cglib/g;
                                    s/org\.powermock\.api\.mockito\.repackaged\.asm/org.objectweb.asm/g'

# Assumes different JUnit version
rm modules/module-impl/junit4-common/src/test/java/org/powermock/modules/junit4/common/internal/impl/JUnitVersionTest.java

# StackOverflow in koji
sed -i '/shouldLoadClassAndOverrideMethodGreaterThanJvmLimit/i@org.junit.Ignore' \
    core/src/test/java/org/powermock/core/transformers/impl/ClassMockTransformerTest.java

# Disable modules that we cannot build (yet).
%pom_disable_module module-test modules
%pom_disable_module junit4-legacy modules/module-impl
%pom_disable_module junit4-rule-agent modules/module-impl
%pom_disable_module junit3 modules/module-impl
%pom_disable_module testng-agent modules/module-impl
%pom_disable_module agent modules/module-impl
%pom_disable_module examples
%pom_disable_module release
%pom_disable_module classloading-xstream classloading
%pom_disable_module mockito2 api

%pom_remove_plugin :rat-maven-plugin
%pom_remove_plugin :maven-source-plugin
%pom_xpath_remove "pom:plugin[pom:artifactId='maven-javadoc-plugin']/pom:executions"

%mvn_package :powermock-core core
%mvn_package :powermock-classloading-base core
%mvn_package :powermock-classloading-objenesis core
%mvn_package :powermock-module-junit4 junit4
%mvn_package :powermock-module-junit4-rule junit4
%mvn_package :powermock-module-junit4-common junit4
%mvn_package :powermock-api-mockito api-mockito
%mvn_package :powermock-api-mockito-common api-mockito
%mvn_package :powermock-api-support api-support
%mvn_package :powermock-api-easymock api-easymock
%mvn_package :powermock-reflect reflect
%mvn_package :powermock-module-testng testng
%mvn_package :powermock-module-testng-common testng

%mvn_package org.powermock.tests: __noinstall

# poms are not needed by anything
%mvn_package ::pom: __noinstall

%build
%mvn_build

%install
%mvn_install

%files common
%dir %{_javadir}/%{name}
%license LICENSE.txt
%files reflect -f .mfiles-reflect
%files core -f .mfiles-core
%files junit4 -f .mfiles-junit4
%files api-support -f .mfiles-api-support
%files api-mockito -f .mfiles-api-mockito
%license api/mockito2/src/main/java/org/powermock/api/mockito/repackaged/Mockito-LICENSE.txt
%files api-easymock -f .mfiles-api-easymock
%files testng -f .mfiles-testng

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.6.5-9
- Escape macros in %%changelog

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 10 2017 Michael Simacek <msimacek@redhat.com> - 1.6.5-7
- Add license and provides for bundled mockito

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jun 22 2016 Michael Simacek <msimacek@redhat.com> - 1.6.5-4
- Unbundle asm and cglib
- Patch forked mockito

* Fri Jun 17 2016 Michael Simacek <msimacek@redhat.com> - 1.6.5-3
- Skip test that overflows stack in koji

* Wed Jun 01 2016 Michael Simacek <msimacek@redhat.com> - 1.6.5-2
- Enable TestNG module

* Wed Jun 01 2016 Michael Simacek <msimacek@redhat.com> - 1.6.5-1
- Update to upstream version 1.6.5

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 Michael Simacek <msimacek@redhat.com> - 1.6.2-1
- Update to upstream version 1.6.2
- Update upstream URL
- Use upstream tarball since the bundled files are opensource and thus can be
  removed in %%prep

* Tue Jun 10 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.4.12-12
- Fix FTBFS by dropping obsolete junit4 surefire provider and
  changing BR to junit over junit4.
- Resolves RHBZ#1106669.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.12-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 27 2014 Michael Simacek <msimacek@redhat.com> - 1.4.12-10
- Enable api-easymock module

* Fri Mar 21 2014 Michael Simacek <msimacek@redhat.com> - 1.4.12-9
- Use mvn_build
- Drop manual requires
- Use pom macros instead of a patch
- Collapse description into a macro

* Fri Jul 26 2013 Alexander Kurtakov <akurtako@redhat.com> 1.4.12-8
- Build against easymock3.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.4.12-6
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 18 2012 Roman Kennke <rkennke@redhat.com> 1.4.12-4
- Use svn export instead of svn checkout for creating source archive
- Remove 3rd party sources from source archive

* Mon May 07 2012 Roman Kennke <rkennke@redhat.com> 1.4.12-3
- Moved JARs to powermock subdirectory
- Removed .svn directories from created source package
- Removed 3rd party source files from created source package

* Mon Apr 30 2012 Roman Kennke <rkennke@redhat.com> 1.4.12-2
- Added javadoc subpackage

* Tue Apr 24 2012 Roman Kennke <rkennke@redhat.com> 1.4.12-1
- Initial package
